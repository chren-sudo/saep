"""
organizations 数据模型

College  学院
Class    班级
"""

from django.conf import settings
from django.db import models

from apps.base import BaseModel


class College(BaseModel):
    """学院"""

    name = models.CharField(max_length=100, unique=True, verbose_name="学院名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="学院代码")

    class Meta:
        db_table = "colleges"
        verbose_name = "学院"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Class(BaseModel):
    """班级"""

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="classes",
        verbose_name="所属学院",
    )
    name = models.CharField(max_length=100, verbose_name="班级名称")
    grade = models.CharField(max_length=20, verbose_name="年级")
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_classes",
        verbose_name="辅导员",
    )

    class Meta:
        db_table = "classes"
        verbose_name = "班级"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.grade})"
