"""
achievements 序列化器
"""

import os

from rest_framework import serializers

from apps.evaluations.models import EvaluationBatch

from .models import Achievement, AchievementCategory, AuditRecord


# ============================================================
# AchievementCategory
# ============================================================

class AchievementCategorySerializer(serializers.ModelSerializer):
    """成果分类 — 读（列表/详情）"""

    class Meta:
        model = AchievementCategory
        fields = ("id", "name", "sort_order", "created_at", "updated_at")
        read_only_fields = fields


class AchievementCategoryWriteSerializer(serializers.ModelSerializer):
    """成果分类 — 写（新增/编辑）"""

    class Meta:
        model = AchievementCategory
        fields = ("name", "sort_order")


# ============================================================
# Achievement
# ============================================================

class AchievementSerializer(serializers.ModelSerializer):
    """成果 — 读（详情）"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    student_name = serializers.CharField(source="student.real_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = (
            "id", "student", "student_name", "student_no", "class_obj", "batch", "batch_name",
            "category", "category_name", "title", "achievement_date", "level",
            "description", "attachment", "attachment_url", "score", "status", "status_display",
            "submitted_at", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_attachment_url(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None


# ============================================================
# Review
# ============================================================

class ReviewListSerializer(serializers.ModelSerializer):
    """待审核列表 — 精简字段，含 has_attachment 标识"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    student_name = serializers.CharField(source="student.real_name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    has_attachment = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = (
            "id", "title", "student_name", "student_no",
            "category_name", "level", "has_attachment",
            "status", "status_display",
            "achievement_date", "submitted_at", "created_at",
        )
        read_only_fields = fields

    def get_has_attachment(self, obj):
        return bool(obj.attachment)


# ============================================================
# Review Actions
# ============================================================

class ApproveSerializer(serializers.Serializer):
    """审核通过"""

    score = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    comment = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")


class ReturnSerializer(serializers.Serializer):
    """审核退回 — comment 必填，告知退回原因"""

    comment = serializers.CharField(max_length=500, required=True, allow_blank=False)


class RejectSerializer(serializers.Serializer):
    """审核驳回 — comment 必填，驳回必须给出理由"""

    comment = serializers.CharField(max_length=500, required=True, allow_blank=False)


# ============================================================
# AuditRecord
# ============================================================

class AuditRecordSerializer(serializers.ModelSerializer):
    """审核记录 — 只读"""

    review_stage_display = serializers.CharField(source="get_review_stage_display", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditRecord
        fields = ("id", "review_stage", "review_stage_display",
                  "action", "action_display",
                  "score", "comment", "reviewer_name", "created_at")


class AchievementListSerializer(serializers.ModelSerializer):
    """成果 — 读（列表，不含 description/attachment 全文）"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    student_name = serializers.CharField(source="student.real_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)

    class Meta:
        model = Achievement
        fields = (
            "id", "student", "student_name", "student_no", "class_obj", "batch", "batch_name",
            "category", "category_name", "title", "achievement_date", "level",
            "score", "status", "status_display",
            "submitted_at", "created_at",
        )
        read_only_fields = fields


class AchievementWriteSerializer(serializers.ModelSerializer):
    """成果 — 写（新增，仅创建 draft）

    student、class_obj、status 由服务端自动注入，客户端不可传入。

    TASK-013: 仅创建 draft。
    TASK-016: 扩展编辑功能（draft/rejected 可编辑）。
    """

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

    class Meta:
        model = Achievement
        fields = ("batch", "category", "title", "achievement_date",
                  "level", "description", "attachment")

    def validate_batch(self, value):
        if value.status != EvaluationBatch.Status.RUNNING:
            raise serializers.ValidationError(
                f"测评批次「{value.name}」未在进行中，无法提交成果"
            )
        return value

    def validate_attachment(self, value):
        from django.conf import settings

        if value.size > settings.FILE_UPLOAD_MAX_SIZE:
            max_mb = settings.FILE_UPLOAD_MAX_SIZE // 1024 // 1024
            raise serializers.ValidationError(
                f"文件大小不能超过 {max_mb}MB"
            )
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"不支持的文件类型: {ext}，仅允许 {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
        return value

    def validate(self, attrs):
        instance = self.instance  # None = create, 有值 = update

        # ============================================================
        # 编辑时的业务规则
        # ============================================================
        if instance:
            # 1. 仅 draft / rejected 可编辑
            if instance.status not in (
                Achievement.Status.DRAFT,
                Achievement.Status.REJECTED,
            ):
                raise serializers.ValidationError(
                    f"当前状态「{instance.get_status_display()}」不允许编辑"
                )

            # 2. rejected 状态不允许修改 batch
            if (
                instance.status == Achievement.Status.REJECTED
                and "batch" in attrs
            ):
                raise serializers.ValidationError(
                    {"batch": "驳回状态不允许修改测评批次"}
                )

        # ============================================================
        # achievement_date vs batch 时间范围校验
        # ============================================================
        batch = attrs.get("batch", instance.batch if instance else None)
        achievement_date = attrs.get(
            "achievement_date",
            instance.achievement_date if instance else None,
        )
        if achievement_date and batch:
            if achievement_date < batch.start_time.date():
                raise serializers.ValidationError(
                    {"achievement_date": "获得日期早于批次开始时间"}
                )
            if achievement_date > batch.end_time.date():
                raise serializers.ValidationError(
                    {"achievement_date": "获得日期晚于批次结束时间"}
                )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["student"] = request.user
        validated_data["class_obj"] = request.user.student_class
        validated_data["status"] = Achievement.Status.DRAFT
        return Achievement.objects.create(**validated_data)
