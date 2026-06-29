"""
statistics 业务逻辑
"""

from django.db import transaction
from django.db.models import Sum

from apps.achievements.models import Achievement
from apps.accounts.models import User

from .models import ScoreSummary


def summarize_batch_class(batch_id, class_id):
    """汇总指定批次+班级的 approved 成果分数，写入 ScoreSummary

    Args:
        batch_id: EvaluationBatch ID
        class_id: Class ID

    Returns:
        dict: {"student_count": int}
    """
    results = (
        Achievement.objects
        .filter(
            batch_id=batch_id,
            class_obj_id=class_id,
            status=Achievement.Status.APPROVED,
        )
        .values("student_id")
        .annotate(total=Sum("score"))
        .order_by()
    )

    with transaction.atomic():
        count = 0
        for row in results:
            ScoreSummary.objects.update_or_create(
                student_id=row["student_id"],
                batch_id=batch_id,
                defaults={"total_score": row["total"] or 0},
            )
            count += 1

    return {"student_count": count}


def rank_batch_class(batch_id, class_id):
    """对指定批次+班级的学生按 total_score 降序计算排名

    竞赛排名法: 同分同排名，后续排名留空位 (1,2,2,4)。
    """
    summaries = list(
        ScoreSummary.objects
        .filter(batch_id=batch_id, student__student_class_id=class_id)
        .select_related("student")
        .order_by("-total_score", "student__student_no")
    )

    if not summaries:
        return {"ranked_count": 0}

    rank = 0
    prev_score = None
    skip = 0

    for s in summaries:
        skip += 1
        if s.total_score != prev_score:
            rank = skip  # 留空位
            prev_score = s.total_score
        s.ranking = rank

    ScoreSummary.objects.bulk_update(summaries, ["ranking"])

    return {"ranked_count": len(summaries)}
