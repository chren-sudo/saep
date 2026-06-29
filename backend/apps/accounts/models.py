"""
accounts 数据模型
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型

    继承 Django AbstractUser。
    TASK-002.5: real_name / phone
    TASK-006:   student_no / employee_no / status
    TASK-006.5: student_class (FK → Class)
    TODO:       avatar（TASK-018 文件上传模块统一实现）
    """

    real_name = models.CharField(max_length=50, blank=True, default="", verbose_name="真实姓名")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机号")
    student_no = models.CharField(max_length=30, blank=True, default="", verbose_name="学号")
    employee_no = models.CharField(max_length=30, blank=True, default="", verbose_name="工号")
    status = models.BooleanField(default=True, verbose_name="启用状态")
    student_class = models.ForeignKey(
        "organizations.Class",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="所属班级",
    )

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.real_name or '-'})"
