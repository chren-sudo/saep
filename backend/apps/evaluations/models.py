"""
evaluations 数据模型

EvaluationBatch  测评批次
"""

from django.db import models

from apps.base import BaseModel


class EvaluationBatch(BaseModel):
    """测评批次"""

    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "未开始"
        RUNNING = 1, "进行中"
        FINISHED = 2, "已结束"

    name = models.CharField(max_length=100, verbose_name="批次名称")
    description = models.TextField(blank=True, default="", verbose_name="批次说明")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.NOT_STARTED,
        verbose_name="状态",
    )

    class Meta:
        db_table = "evaluation_batches"
        verbose_name = "测评批次"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
