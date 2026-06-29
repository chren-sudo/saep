"""
organizations 序列化器
"""

from rest_framework import serializers

from apps.accounts.models import User


class EvaluatorListSerializer(serializers.ModelSerializer):
    """测评小组成员列表"""

    class Meta:
        model = User
        fields = ("id", "username", "real_name", "student_no")


class ClassStudentSerializer(serializers.ModelSerializer):
    """班级学生列表"""

    is_evaluator = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "real_name", "student_no",
                  "phone", "is_active", "is_evaluator", "date_joined")

    def get_is_evaluator(self, obj):
        # prefetch_related("groups") 已在 get_queryset 中设置，避免 N+1
        return any(g.name == "evaluator" for g in obj.groups.all())
