"""
achievements 视图
"""

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.accounts.permissions import IsCollegeAdminOrSuperAdmin, IsStudentRole

from .models import Achievement, AchievementCategory, AuditRecord


# ============================================================
# 共享查询 — AchievementViewSet + ExportViewSet 共用
# ============================================================

def _get_achievement_queryset(user):
    """按角色确定 Achievement 数据范围"""
    qs = Achievement.objects.select_related(
        "student", "student__student_class", "category", "batch"
    )
    group_names = set(user.groups.values_list("name", flat=True))

    if "super_admin" in group_names or "college_admin" in group_names:
        return qs

    if "evaluator" in group_names:
        class_obj = user.student_class
        if class_obj:
            return qs.filter(class_obj=class_obj)
        return qs.none()

    if "counselor" in group_names:
        class_objs = user.managed_classes.all()
        if class_objs.exists():
            return qs.filter(class_obj__in=class_objs)
        return qs.none()

    if "student" in group_names:
        return qs.filter(student=user)

    return qs.none()
from .serializers import (
    AchievementCategorySerializer,
    AchievementCategoryWriteSerializer,
    AchievementListSerializer,
    AchievementSerializer,
    AchievementWriteSerializer,
    ApproveSerializer,
    AuditRecordSerializer,
    RejectSerializer,
    ReturnSerializer,
    ReviewListSerializer,
)


class AchievementCategoryViewSet(ModelViewSet):
    """成果分类 CRUD"""

    queryset = AchievementCategory.objects.all()
    ordering = ["sort_order", "id"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsCollegeAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AchievementCategoryWriteSerializer
        return AchievementCategorySerializer


class AchievementViewSet(ModelViewSet):
    """成果 CRUD

    TASK-013: 开放 create (POST)，创建 draft。
    TASK-014: 开放 list (GET)，按角色返回不同数据范围 + 筛选 + 搜索。
    TASK-015: 开放 retrieve (GET)。
    TASK-016: 开放 update (PUT)，仅 draft/rejected 可编辑。
    TASK-017: 开放 destroy (DELETE)，仅 draft/rejected 可删。
    """

    queryset = Achievement.objects.select_related("student", "category", "batch")
    filterset_fields = ["status", "batch", "class_obj", "category"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "score", "achievement_date"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "submit"):
            return [IsAuthenticated(), IsStudentRole()]
        # list/retrieve — 所有已认证角色可访问，数据范围由 get_queryset 控制
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AchievementWriteSerializer
        if self.action == "list":
            return AchievementListSerializer
        return AchievementSerializer

    def get_queryset(self):
        return _get_achievement_queryset(self.request.user)

    def perform_destroy(self, instance):
        """仅 draft / rejected 可删除"""
        from rest_framework.exceptions import ValidationError

        if instance.status not in (
            Achievement.Status.DRAFT,
            Achievement.Status.REJECTED,
        ):
            raise ValidationError(
                f"当前状态「{instance.get_status_display()}」不允许删除"
            )
        instance.delete()

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """提交审核 — draft → submitted"""
        achievement = self.get_object()

        if achievement.status != Achievement.Status.DRAFT:
            raise ValidationError(
                f"当前状态「{achievement.get_status_display()}」不允许提交，仅草稿可提交"
            )

        from django.utils import timezone
        achievement.status = Achievement.Status.SUBMITTED
        achievement.submitted_at = timezone.now()
        achievement.save(update_fields=["status", "submitted_at"])

        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {"id": achievement.id, "status": achievement.status},
            }
        )

    @action(detail=True, methods=["get"], url_path="audit-records")
    def audit_records(self, request, pk=None):
        """审核日志

        GET /api/v1/achievements/{id}/audit-records/
        返回该成果的完整审核时间线（按时间升序）。
        """
        achievement = self.get_object()
        records = achievement.audit_records.all()
        serializer = AuditRecordSerializer(records, many=True)
        return Response(
            {
                "code": 0,
                "message": "success",
                "data": serializer.data,
            }
        )


class ReviewViewSet(ListModelMixin, GenericViewSet):
    """待审核列表 — 仅 GET /reviews/

    审核阶段由当前用户角色自动确定，无需传入 stage 参数。
    - evaluator:  本班 status=submitted
    - counselor:  本班 status=counselor_reviewing
    """

    queryset = Achievement.objects.select_related("student", "category")
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["batch"]

    def get_queryset(self):
        user = self.request.user
        group_names = set(user.groups.values_list("name", flat=True))
        qs = super().get_queryset()

        if "evaluator" in group_names:
            class_obj = user.student_class
            if not class_obj:
                return qs.none()
            return qs.filter(
                class_obj=class_obj,
                status=Achievement.Status.SUBMITTED,
            )

        if "counselor" in group_names:
            class_objs = user.managed_classes.all()
            if not class_objs.exists():
                return qs.none()
            return qs.filter(
                class_obj__in=class_objs,
                status=Achievement.Status.COUNSELOR_REVIEWING,
            )

        return qs.none()

    # ============================================================
    # approve / return / reject 共用权限校验
    # ============================================================

    def _check_review_permission(self, achievement, user):
        """根据角色确定审核状态映射，返回 (allowed_status, new_status, stage)

        数据权限（班级归属）由 get_queryset() 统一控制。
        不在 queryset 范围内 → 404（Resource Hiding）。
        """
        group_names = set(user.groups.values_list("name", flat=True))

        if "evaluator" in group_names:
            return (
                Achievement.Status.SUBMITTED,
                Achievement.Status.COUNSELOR_REVIEWING,
                AuditRecord.ReviewStage.EVALUATOR,
            )

        if "counselor" in group_names:
            return (
                Achievement.Status.COUNSELOR_REVIEWING,
                Achievement.Status.APPROVED,
                AuditRecord.ReviewStage.COUNSELOR,
            )

        raise PermissionDenied("无权执行审核操作")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """审核通过

        evaluator:  submitted → counselor_reviewing
        counselor:  counselor_reviewing → approved
        """
        achievement = self.get_object()

        allowed_status, new_status, stage = self._check_review_permission(
            achievement, request.user
        )

        if achievement.status != allowed_status:
            raise ValidationError(
                f"当前状态「{achievement.get_status_display()}」不允许此操作"
            )

        serializer = ApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score = serializer.validated_data["score"]
        comment = serializer.validated_data.get("comment", "")

        with transaction.atomic():
            achievement.status = new_status
            achievement.score = score
            achievement.save()

            AuditRecord.objects.create(
                achievement=achievement,
                reviewer=request.user,
                reviewer_name=request.user.real_name or request.user.username,
                review_stage=stage,
                action=AuditRecord.Action.APPROVE,
                score=score,
                comment=comment,
            )

        from apps.system.services import write_operation_log
        from apps.system.models import OperationLog
        write_operation_log(
            request.user, request,
            module=OperationLog.Module.REVIEW,
            action=OperationLog.Action.APPROVE,
            detail=f"Achievement #{achievement.id} approved",
        )

        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "id": achievement.id,
                    "status": achievement.status,
                },
            }
        )

    @action(detail=True, methods=["post"], url_path="return")
    def return_achievement(self, request, pk=None):
        """审核退回

        evaluator:  submitted → draft（退回学生）
        counselor:  counselor_reviewing → submitted（退回测评小组）
        """
        achievement = self.get_object()

        allowed_status, _, stage = self._check_review_permission(
            achievement, request.user
        )

        if achievement.status != allowed_status:
            raise ValidationError(
                f"当前状态「{achievement.get_status_display()}」不允许此操作"
            )

        serializer = ReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data["comment"]

        return_targets = {
            AuditRecord.ReviewStage.EVALUATOR: Achievement.Status.DRAFT,
            AuditRecord.ReviewStage.COUNSELOR: Achievement.Status.DRAFT,
        }
        new_status = return_targets[stage]

        with transaction.atomic():
            achievement.status = new_status
            achievement.save()

            AuditRecord.objects.create(
                achievement=achievement,
                reviewer=request.user,
                reviewer_name=request.user.real_name or request.user.username,
                review_stage=stage,
                action=AuditRecord.Action.RETURN,
                score=None,
                comment=comment,
            )

        from apps.system.services import write_operation_log
        from apps.system.models import OperationLog
        write_operation_log(
            request.user, request,
            module=OperationLog.Module.REVIEW,
            action=OperationLog.Action.RETURN,
            detail=f"Achievement #{achievement.id} returned",
        )

        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "id": achievement.id,
                    "status": achievement.status,
                },
            }
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """审核驳回

        evaluator:  submitted → rejected（终态）
        counselor:  counselor_reviewing → rejected（终态）
        """
        achievement = self.get_object()

        allowed_status, _, stage = self._check_review_permission(
            achievement, request.user
        )

        if achievement.status != allowed_status:
            raise ValidationError(
                f"当前状态「{achievement.get_status_display()}」不允许此操作"
            )

        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data["comment"]

        with transaction.atomic():
            achievement.status = Achievement.Status.REJECTED
            achievement.save()

            AuditRecord.objects.create(
                achievement=achievement,
                reviewer=request.user,
                reviewer_name=request.user.real_name or request.user.username,
                review_stage=stage,
                action=AuditRecord.Action.REJECT,
                score=None,
                comment=comment,
            )

        from apps.system.services import write_operation_log
        from apps.system.models import OperationLog
        write_operation_log(
            request.user, request,
            module=OperationLog.Module.REVIEW,
            action=OperationLog.Action.REJECT,
            detail=f"Achievement #{achievement.id} rejected",
        )

        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "id": achievement.id,
                    "status": achievement.status,
                },
            }
        )
