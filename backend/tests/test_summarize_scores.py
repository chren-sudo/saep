"""
TASK-033 成绩汇总 单元测试
"""

from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.achievements.models import Achievement, AchievementCategory
from apps.evaluations.models import EvaluationBatch
from apps.organizations.models import Class, College
from apps.statistics.models import ScoreSummary
from apps.statistics.services import summarize_batch_class
from django.utils import timezone


class SummarizeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")
        cls.other_class = Class.objects.create(college=cls.college, name="c2", grade="2025")

        cls.student = User.objects.create_user(username="s1", password="p", real_name="学生",
                                                student_class=cls.class_obj)
        add_user_role(cls.student, "student")
        cls.student2 = User.objects.create_user(username="s2", password="p", real_name="学生2",
                                                 student_class=cls.class_obj)
        add_user_role(cls.student2, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(), end_time=timezone.now()+timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="c")

        cls.factory = None  # No API, pure logic test

    def _make_approved(self, student, score):
        return Achievement.objects.create(
            student=student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title=f"a-{score}", score=score, status=Achievement.Status.APPROVED,
        )

    # ============================================================
    def test_01_summarize_single_student(self):
        self._make_approved(self.student, 8.5)
        self._make_approved(self.student, 3.0)
        result = summarize_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["student_count"], 1)

        s = ScoreSummary.objects.get(student=self.student, batch=self.batch)
        self.assertEqual(s.total_score, Decimal("11.50"))

    def test_02_summarize_multiple_students(self):
        self._make_approved(self.student, 8.0)
        self._make_approved(self.student2, 6.0)
        result = summarize_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(result["student_count"], 2)

    def test_03_idempotent(self):
        self._make_approved(self.student, 5.0)
        summarize_batch_class(self.batch.id, self.class_obj.id)
        summarize_batch_class(self.batch.id, self.class_obj.id)
        self.assertEqual(ScoreSummary.objects.filter(
            student=self.student, batch=self.batch).count(), 1)

    def test_04_skips_non_approved(self):
        Achievement.objects.create(
            student=self.student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title="draft", score=100, status=Achievement.Status.DRAFT,
        )
        Achievement.objects.create(
            student=self.student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title="submitted", score=100, status=Achievement.Status.SUBMITTED,
        )
        summarize_batch_class(self.batch.id, self.class_obj.id)
        self.assertFalse(ScoreSummary.objects.filter(
            student=self.student, batch=self.batch).exists())

    def test_05_only_target_class(self):
        self._make_approved(self.student, 8.0)
        # other_class has no approved → should be 0
        result = summarize_batch_class(self.batch.id, self.other_class.id)
        self.assertEqual(result["student_count"], 0)

    def test_06_ranking_not_set(self):
        self._make_approved(self.student, 5.0)
        summarize_batch_class(self.batch.id, self.class_obj.id)
        s = ScoreSummary.objects.get(student=self.student, batch=self.batch)
        self.assertEqual(s.ranking, 0)

    def test_07_recalculate_updates(self):
        self._make_approved(self.student, 5.0)
        summarize_batch_class(self.batch.id, self.class_obj.id)
        # Add another approved
        self._make_approved(self.student, 3.0)
        summarize_batch_class(self.batch.id, self.class_obj.id)
        s = ScoreSummary.objects.get(student=self.student, batch=self.batch)
        self.assertEqual(s.total_score, Decimal("8.00"))
