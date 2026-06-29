"""
evaluations 序列化器
"""

from rest_framework import serializers

from .models import EvaluationBatch


class EvaluationBatchSerializer(serializers.ModelSerializer):
    """测评批次 — 读（列表/详情）"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EvaluationBatch
        fields = ("id", "name", "description", "start_time", "end_time",
                  "status", "status_display", "created_at", "updated_at")
        read_only_fields = fields


class EvaluationBatchWriteSerializer(serializers.ModelSerializer):
    """测评批次 — 写（新增/编辑）

    status 不接受客户端传入。
    新增时默认 status=0（未开始），编辑时仅更新名称/时间。

    TODO: 后续版本根据 start_time/end_time 自动计算 status，
          避免时间与 status 不一致。
    """

    class Meta:
        model = EvaluationBatch
        fields = ("name", "description", "start_time", "end_time")

    def validate(self, attrs):
        # 编辑时 attrs 可能缺少 start_time 或 end_time，从 instance 补全
        instance = self.instance
        start = attrs.get("start_time", instance.start_time if instance else None)
        end = attrs.get("end_time", instance.end_time if instance else None)
        if start and end and start >= end:
            raise serializers.ValidationError("开始时间必须早于结束时间")
        return attrs
