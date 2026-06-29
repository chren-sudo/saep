"""
organizations 视图
"""

from django.http import Http404
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, remove_user_role

from .models import Class
from .serializers import ClassStudentSerializer, EvaluatorListSerializer


# ============================================================
# 权限公共方法（TASK-025 + TASK-026 共用）
# TECH-DEBT-010: college_admin 学院权限收敛时仅修改此函数。
# ============================================================

def _get_managed_class(class_id, user):
    """获取用户有权访问的班级，不在范围 → 404"""
    if user.groups.filter(name="counselor").exists():
        if not user.managed_classes.filter(id=class_id).exists():
            raise Http404
    elif not user.groups.filter(name__in=["college_admin", "super_admin"]).exists():
        raise Http404

    try:
        return Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        raise Http404


# ============================================================
# TASK-025: EvaluatorViewSet
# ============================================================

class EvaluatorViewSet(GenericViewSet):
    """测评小组管理

    GET    /classes/{class_id}/evaluators/
    POST   /classes/{class_id}/evaluators/
    DELETE /classes/{class_id}/evaluators/{user_id}/
    """

    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._class_obj = _get_managed_class(int(kwargs["class_id"]), request.user)

    def list(self, request, class_id=None):
        evaluators = User.objects.filter(
            student_class=self._class_obj,
            groups__name="evaluator",
        )
        serializer = EvaluatorListSerializer(evaluators, many=True)
        return Response(
            {"code": 0, "message": "success", "data": serializer.data}
        )

    def create(self, request, class_id=None):
        from rest_framework.exceptions import ValidationError

        user_id = request.data.get("user_id")
        if not user_id:
            raise ValidationError("user_id 不能为空")

        try:
            student = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404

        if student.student_class_id != self._class_obj.id:
            raise ValidationError("该学生不属于本班")

        if not student.groups.filter(name="student").exists():
            raise ValidationError("该用户不是学生")

        add_user_role(student, "evaluator")

        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {"id": student.id, "real_name": student.real_name},
            }
        )

    def destroy(self, request, class_id=None, pk=None):
        from rest_framework.exceptions import ValidationError

        try:
            evaluator = User.objects.get(
                id=pk,
                student_class=self._class_obj,
            )
        except User.DoesNotExist:
            raise Http404

        if not evaluator.groups.filter(name="evaluator").exists():
            raise ValidationError("该用户不是测评小组成员")

        remove_user_role(evaluator, "evaluator")

        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# TASK-026: ClassStudentViewSet
# ============================================================

class ClassStudentViewSet(GenericViewSet, ListModelMixin):
    """班级学生管理 — 仅 GET /classes/{class_id}/students/"""

    permission_classes = [IsAuthenticated]
    search_fields = ["real_name", "student_no", "username"]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._class_obj = _get_managed_class(int(kwargs["class_id"]), request.user)

    def get_queryset(self):
        return User.objects.filter(
            student_class=self._class_obj,
            groups__name="student",
        ).prefetch_related("groups").order_by("student_no")

    def get_serializer_class(self):
        return ClassStudentSerializer
