"""
notifications 序列化器
"""

from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    """通知公告 — create/list/retrieve 共用"""

    publisher_name = serializers.CharField(source="publisher.real_name", read_only=True)

    class Meta:
        model = Announcement
        fields = ("id", "title", "content", "publisher", "publisher_name",
                  "created_at", "updated_at")
        read_only_fields = ("id", "publisher", "publisher_name", "created_at", "updated_at")
