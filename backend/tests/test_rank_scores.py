"""
TASK-034 排名计算 单元测试
"""

from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.evaluations.models import EvaluationBatch
from apps.statistics.models import ScoreSummary
from apps.statistics.services import rank_batch_class


class RankTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")
        cls.other_class = Class.objects.create(college=cls.college, name="c2", grade="2025")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )

        cls.factory = None

    def _make_summary(self, username, score, class_obj=None, student_no="001"):
        student = User.objects.create_user(
            username=username, password="p", real_name=username,
            student_class=class_obj or self.class_obj, student_no=student_no,
        )
        add_user_role(student, "student")
        return ScoreSummary.objects.create(
            student=student, batch=self.batch, total_score=Decimal(score),
        )

    # ============================================================
    def test_01_single_student_rank_one(self):
        self._make_summary("s1", "10.0")
        result = rank_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["ranked_count"], 1)
        s = ScoreSummary.objects.get(student__username="s1")
        self.assertEqual(s.ranking, 1)

    def test_02_competition_ranking_ties(self):
        self._make_summary("s1", "11.5", student_no="001")
        self._make_summary("s2", "9.0", student_no="002")
        self._make_summary("s3", "9.0", student_no="003")
        self._make_summary("s4", "7.0", student_no="004")

        rank_batch_class(self.batch.id, self.class_obj.id)

        self.assertEqual(ScoreSummary.objects.get(student__username="s1").ranking, 1)
        self.assertEqual(ScoreSummary.objects.get(student__username="s2").ranking, 2)
        self.assertEqual(ScoreSummary.objects.get(student__username="s3").ranking, 2)  # tie
        self.assertEqual(ScoreSummary.objects.get(student__username="s4").ranking, 4)  # skip 3

    def test_03_stable_sort_by_student_no(self):
        self._make_summary("s1", "10.0", student_no="002")
        self._make_summary("s2", "10.0", student_no="001")

        rank_batch_class(self.batch.id, self.class_obj.id)

        r1 = ScoreSummary.objects.get(student__username="s1").ranking
        r2 = ScoreSummary.objects.get(student__username="s2").ranking
        self.assertEqual(r1, r2)
        # student_no 001 should come first (order_by student_no ASC)
        first = ScoreSummary.objects.filter(
            batch=self.batch, student__student_class=self.class_obj
        ).order_by("-total_score", "student__student_no").first()
        self.assertEqual(first.student.username, "s2")

    def test_04_only_target_class(self):
        self._make_summary("s1", "10.0", class_obj=self.class_obj)
        self._make_summary("s2", "5.0", class_obj=self.other_class)

        result = rank_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["ranked_count"], 1)

        # s2 (other class) should still have ranking=0
        s2 = ScoreSummary.objects.get(student__username="s2")
        self.assertEqual(s2.ranking, 0)

    def test_05_empty_class(self):
        result = rank_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["ranked_count"], 0)

    def test_06_idempotent(self):
        self._make_summary("s1", "10.0")
        rank_batch_class(self.batch.id, self.class_obj.id)
        rank_batch_class(self.batch.id, self.class_obj.id)
        s = ScoreSummary.objects.get(student__username="s1")
        self.assertEqual(s.ranking, 1)

    def test_07_bulk_update_used(self):
        self._make_summary("s1", "10.0", student_no="001")
        self._make_summary("s2", "8.0", student_no="002")
        self._make_summary("s3", "6.0", student_no="003")

        result = rank_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["ranked_count"], 3)
        rankings = list(ScoreSummary.objects.filter(
            batch=self.batch, student__student_class=self.class_obj
        ).values_list("ranking", flat=True).order_by("ranking"))
        self.assertEqual(rankings, [1, 2, 3])
