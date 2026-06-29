"""
成绩汇总命令

对指定批次+班级的 approved 成果进行 SUM 聚合，写入 ScoreSummary。

用法：
    python manage.py summarize_scores --batch=3 --class=3
    python manage.py summarize_scores --batch=3  (该批次所有班级)

公示结束时可编程调用:
    from apps.statistics.services import summarize_batch_class
    summarize_batch_class(batch_id=3, class_id=3)
"""

from django.core.management.base import BaseCommand

from apps.statistics.services import summarize_batch_class


class Command(BaseCommand):
    help = "汇总指定批次+班级的 approved 成果分数，写入 ScoreSummary"

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, required=True, help="测评批次 ID")
        parser.add_argument("--class", type=int, dest="class_id", help="班级 ID（可选，不传则汇总该批次所有班级）")

    def handle(self, *args, **options):
        batch_id = options["batch"]
        class_id = options.get("class_id")

        if class_id:
            result = summarize_batch_class(batch_id, class_id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"批次 {batch_id} 班级 {class_id}: "
                    f"汇总 {result['student_count']} 名学生"
                )
            )
        else:
            total = 0
            from apps.organizations.models import Class as Cls
            for cls in Cls.objects.all():
                result = summarize_batch_class(batch_id, cls.id)
                total += result["student_count"]
            self.stdout.write(self.style.SUCCESS(f"批次 {batch_id}: 汇总 {total} 名学生"))
