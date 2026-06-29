"""
publicity 数据模型

PublicNotice  公示
"""

from django.db import models

from apps.base import BaseModel


class PublicNotice(BaseModel):
    """公示

    一个班级在一个批次中发布一条公示。
    """

    class Status(models.IntegerChoices):
        DRAFT = 0, "草稿"
        PUBLISHED = 1, "公示中"
        CLOSED = 2, "已结束"

    batch = models.ForeignKey(
        "evaluations.EvaluationBatch",
        on_delete=models.CASCADE,
        related_name="public_notices",
        verbose_name="测评批次",
    )
    class_obj = models.ForeignKey(
        "organizations.Class",
        on_delete=models.CASCADE,
        related_name="public_notices",
        verbose_name="班级",
    )
    title = models.CharField(max_length=200, verbose_name="公示标题")
    start_time = models.DateTimeField(verbose_name="公示开始时间")
    end_time = models.DateTimeField(verbose_name="公示结束时间")
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="状态",
    )

    class Meta:
        db_table = "public_notices"
        verbose_name = "公示"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "class_obj"],
                name="unique_batch_class_notice",
            )
        ]

    def __str__(self):
        return self.title
