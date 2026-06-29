"""
notifications 数据模型

Announcement  通知公告
"""

from django.conf import settings
from django.db import models

from apps.base import BaseModel


class Announcement(BaseModel):
    """通知公告"""

    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="正文")
    publisher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
        verbose_name="发布人",
    )

    class Meta:
        db_table = "announcements"
        verbose_name = "通知公告"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
