"""
statistics 序列化器
"""

from rest_framework import serializers

from .models import ScoreSummary


class ScoreSummarySerializer(serializers.ModelSerializer):
    """我的成绩 / 班级排名"""

    batch_name = serializers.CharField(source="batch.name", read_only=True)
    student_name = serializers.CharField(source="student.real_name", read_only=True)
    student_no = serializers.CharField(source="student.student_no", read_only=True)
    class_name = serializers.CharField(source="student.student_class.name", read_only=True)

    class Meta:
        model = ScoreSummary
        fields = ("id", "student", "student_name", "student_no", "class_name",
                  "batch", "batch_name", "total_score", "ranking")
        read_only_fields = fields
