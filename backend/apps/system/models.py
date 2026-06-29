"""
system 数据模型

OperationLog  操作日志
"""

from django.conf import settings
from django.db import models


class OperationLog(models.Model):
    """操作日志 — 只增不改，不继承 BaseModel"""

    class Module(models.TextChoices):
        AUTH = "auth", "认证"
        ACHIEVEMENT = "achievement", "成果"
        REVIEW = "review", "审核"
        PUBLICITY = "publicity", "公示"
        STATISTICS = "statistics", "统计"
        EXPORT = "export", "导出"
        SYSTEM = "system", "系统"

    class Action(models.TextChoices):
        LOGIN = "login", "登录"
        CREATE = "create", "新增"
        UPDATE = "update", "修改"
        DELETE = "delete", "删除"
        APPROVE = "approve", "通过"
        RETURN = "return", "退回"
        REJECT = "reject", "驳回"
        PUBLISH = "publish", "发布"
        CLOSE = "close", "结束"
        EXPORT = "export", "导出"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="operation_logs",
        verbose_name="操作人",
    )
    module = models.CharField(max_length=20, choices=Module.choices, verbose_name="模块")
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name="动作")
    detail = models.TextField(blank=True, default="", verbose_name="操作说明")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        db_table = "operation_logs"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_module_display()}] {self.get_action_display()}"
