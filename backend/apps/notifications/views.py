"""
notifications 视图
"""

from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.accounts.permissions import IsCollegeAdminOrSuperAdmin

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin):
    """通知公告

    TASK-038: POST /announcements — 发布
    TASK-039: GET /announcements — 列表
    """

    queryset = Announcement.objects.select_related("publisher")
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCollegeAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(publisher=self.request.user)
