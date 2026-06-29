"""
排名计算命令

对指定批次+班级的 ScoreSummary 按 total_score 降序计算 ranking。

用法：
    python manage.py rank_scores --batch=3 --class=3
    python manage.py rank_scores --batch=3  (该批次所有班级)
"""

from django.core.management.base import BaseCommand

from apps.statistics.services import rank_batch_class


class Command(BaseCommand):
    help = "计算指定批次+班级的排名，写入 ScoreSummary.ranking"

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, required=True)
        parser.add_argument("--class", type=int, dest="class_id")

    def handle(self, *args, **options):
        batch_id = options["batch"]
        class_id = options.get("class_id")

        if class_id:
            result = rank_batch_class(batch_id, class_id)
            self.stdout.write(self.style.SUCCESS(f"排名完成: {result['ranked_count']} 人"))
        else:
            total = 0
            from apps.organizations.models import Class as Cls
            for cls in Cls.objects.all():
                result = rank_batch_class(batch_id, cls.id)
                total += result["ranked_count"]
            self.stdout.write(self.style.SUCCESS(f"排名完成: {total} 人"))
