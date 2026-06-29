"""
achievements 数据模型

AchievementCategory  成果分类
Achievement          成果
"""

import os
import uuid

from django.conf import settings
from django.db import models

from apps.base import BaseModel


def _rename_attachment(instance, filename):
    """UUID + 原文件名，避免同名冲突"""
    from datetime import datetime

    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    now = datetime.now()
    safe_name = name.replace(" ", "_")[:50]
    return f"uploads/{now:%Y}/{now:%m}/{uuid.uuid4().hex}_{safe_name}{ext}"


class AchievementCategory(BaseModel):
    """成果分类（学科竞赛、科研成果、社会实践、志愿服务、文体活动）"""

    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    sort_order = models.IntegerField(default=0, verbose_name="排序")

    class Meta:
        db_table = "achievement_categories"
        verbose_name = "成果分类"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class Achievement(BaseModel):
    """成果"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        SUBMITTED = "submitted", "已提交"
        REVIEWING = "reviewing", "测评小组审核中"
        COUNSELOR_REVIEWING = "counselor_reviewing", "待辅导员终审"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已驳回"

    # FK
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="学生",
    )
    class_obj = models.ForeignKey(
        "organizations.Class",
        on_delete=models.PROTECT,
        related_name="achievements",
        verbose_name="班级",
    )
    batch = models.ForeignKey(
        "evaluations.EvaluationBatch",
        on_delete=models.PROTECT,
        related_name="achievements",
        verbose_name="测评批次",
    )
    category = models.ForeignKey(
        AchievementCategory,
        on_delete=models.PROTECT,
        related_name="achievements",
        verbose_name="成果分类",
    )

    # 业务字段
    title = models.CharField(max_length=200, verbose_name="成果名称")
    achievement_date = models.DateField(null=True, blank=True, verbose_name="获得日期")
    level = models.CharField(max_length=20, blank=True, default="", verbose_name="成果等级")
    description = models.TextField(blank=True, default="", verbose_name="成果说明")
    attachment = models.FileField(upload_to=_rename_attachment, blank=True, verbose_name="附件")

    # 审核字段
    score = models.FloatField(null=True, blank=True, verbose_name="认定分数")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="状态",
    )
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")

    class Meta:
        db_table = "achievements"
        verbose_name = "成果"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["batch"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["class_obj", "status"]),
            models.Index(fields=["batch", "class_obj"]),
        ]

    def __str__(self):
        return self.title


class AuditRecord(BaseModel):
    """审核记录

    每次审核操作（approve / reject / return）创建一条记录。
    创建后不可修改、不可删除。

    achievement FK CASCADE — 技术债：
        删除 rejected 成果时审核轨迹丢失。
        V2.0 评估改为 PROTECT 或 SET_NULL。
        OperationLog 作为跨模型审计补充。

    TODO V2.0: 增加 status_before / status_after 字段，
              精确记录每次审核操作前后的 Achievement.status。
    """

    class ReviewStage(models.TextChoices):
        EVALUATOR = "evaluator", "测评小组"
        COUNSELOR = "counselor", "辅导员"

    class Action(models.TextChoices):
        APPROVE = "approve", "通过"
        REJECT = "reject", "驳回"
        RETURN = "return", "退回"

    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="audit_records",
        verbose_name="成果",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_records",
        verbose_name="审核人",
    )
    reviewer_name = models.CharField(
        max_length=50, default="", verbose_name="审核人姓名（快照）",
    )
    review_stage = models.CharField(
        max_length=20, choices=ReviewStage.choices, verbose_name="审核阶段",
    )
    action = models.CharField(
        max_length=20, choices=Action.choices, verbose_name="动作",
    )
    score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="认定分数",
    )
    comment = models.CharField(
        max_length=500, blank=True, default="", verbose_name="审核意见",
    )

    class Meta:
        db_table = "audit_records"
        verbose_name = "审核记录"
        verbose_name_plural = verbose_name
        ordering = ["created_at"]
        # FK 索引由 Django 自动创建，无需手动定义

    def __str__(self):
        return f"[{self.get_review_stage_display()}] {self.get_action_display()}"
