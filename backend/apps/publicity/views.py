"""
publicity 视图
"""

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsCounselorRole

from .models import PublicNotice
from .serializers import PublicNoticeSerializer, PublicNoticeWriteSerializer


class PublicNoticeViewSet(ModelViewSet):
    """公示管理

    TASK-029: create (生成公示)
    TASK-030: publish action (发布)
    TASK-031: close action (结束)
    """

    queryset = PublicNotice.objects.select_related("batch", "class_obj")

    def get_permissions(self):
        if self.action in ("create", "publish", "close"):
            return [IsAuthenticated(), IsCounselorRole()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return PublicNoticeWriteSerializer
        return PublicNoticeSerializer

    def get_queryset(self):
        """counselor 仅查看/操作管理班级的公示"""
        qs = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name="counselor").exists():
            return qs.filter(class_obj__in=user.managed_classes.all())
        # super_admin / college_admin → 全部
        return qs

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()

    # ============================================================
    # publish / close 共用
    # ============================================================

    def _check_notice_status(self, notice, expected):
        if notice.status != expected:
            raise ValidationError(
                f"当前状态「{notice.get_status_display()}」不允许此操作"
            )

    # ============================================================
    # TASK-030: publish
    # ============================================================

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """发布公示 — draft → published"""
        notice = self.get_object()
        self._check_notice_status(notice, PublicNotice.Status.DRAFT)

        notice.status = PublicNotice.Status.PUBLISHED
        notice.save(update_fields=["status"])

        serializer = self.get_serializer(notice)
        return Response(
            {"code": 0, "message": "success", "data": serializer.data}
        )

    # ============================================================
    # TASK-031: close
    # ============================================================

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """结束公示 — published → closed"""
        notice = self.get_object()
        self._check_notice_status(notice, PublicNotice.Status.PUBLISHED)

        notice.status = PublicNotice.Status.CLOSED
        notice.save(update_fields=["status"])

        serializer = self.get_serializer(notice)
        return Response(
            {"code": 0, "message": "success", "data": serializer.data}
        )
