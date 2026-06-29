"""
publicity 序列化器
"""

from django.db import IntegrityError
from rest_framework import serializers

from apps.achievements.models import Achievement

from .models import PublicNotice


class PublicNoticeWriteSerializer(serializers.ModelSerializer):
    """公示 — 写（生成公示）"""

    class Meta:
        model = PublicNotice
        fields = ("batch", "class_obj", "title", "start_time", "end_time")

    def validate(self, attrs):
        batch = attrs["batch"]
        class_obj = attrs["class_obj"]
        start = attrs["start_time"]
        end = attrs["end_time"]

        # 时间校验
        if start >= end:
            raise serializers.ValidationError("开始时间必须早于结束时间")

        # 唯一性校验（友好提示）
        if PublicNotice.objects.filter(batch=batch, class_obj=class_obj).exists():
            raise serializers.ValidationError("该班级在此批次已存在公示")

        # 无 approved 成果不可生成公示
        if not Achievement.objects.filter(
            batch=batch, class_obj=class_obj, status=Achievement.Status.APPROVED
        ).exists():
            raise serializers.ValidationError("当前班级暂无已审核通过成果，无法生成公示")

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("该班级在此批次已存在公示")


class PublicNoticeSerializer(serializers.ModelSerializer):
    """公示 — 读"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    class_name = serializers.CharField(source="class_obj.name", read_only=True)
    approved_count = serializers.SerializerMethodField()

    class Meta:
        model = PublicNotice
        fields = ("id", "batch", "batch_name", "class_obj", "class_name",
                  "title", "start_time", "end_time", "status", "status_display",
                  "approved_count", "created_at", "updated_at")
        read_only_fields = fields

    def get_approved_count(self, obj):
        from apps.achievements.models import Achievement
        return Achievement.objects.filter(
            batch=obj.batch, class_obj=obj.class_obj,
            status=Achievement.Status.APPROVED,
        ).count()
