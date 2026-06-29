"""
statistics 数据模型

ScoreSummary  成绩汇总
"""

from django.conf import settings
from django.db import models

from apps.base import BaseModel


class ScoreSummary(BaseModel):
    """成绩汇总 — 按学生+批次聚合"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="score_summaries",
        verbose_name="学生",
    )
    batch = models.ForeignKey(
        "evaluations.EvaluationBatch",
        on_delete=models.CASCADE,
        related_name="score_summaries",
        verbose_name="测评批次",
    )
    total_score = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="总得分",
    )
    ranking = models.PositiveIntegerField(
        default=0, verbose_name="班级排名（0=未排名）",
    )

    class Meta:
        db_table = "score_summaries"
        verbose_name = "成绩汇总"
        verbose_name_plural = verbose_name
        ordering = ["batch", "-total_score"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "batch"],
                name="unique_student_batch_score",
            )
        ]
        indexes = [
            models.Index(fields=["student", "batch"]),
            models.Index(fields=["batch", "ranking"]),
        ]

    def __str__(self):
        return f"{self.student.real_name} - {self.batch.name}: {self.total_score}"
