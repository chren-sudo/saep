"""
TASK-035 我的成绩 单元测试
"""

from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.evaluations.models import EvaluationBatch
from apps.statistics.models import ScoreSummary
from apps.statistics.views import ScoreViewSet


class MyScoresTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")

        cls.student1 = User.objects.create_user(username="s1", password="p", real_name="张三",
                                                 student_class=cls.class_obj, student_no="001")
        add_user_role(cls.student1, "student")

        cls.student2 = User.objects.create_user(username="s2", password="p", real_name="李四",
                                                 student_class=cls.class_obj, student_no="002")
        add_user_role(cls.student2, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.batch2 = EvaluationBatch.objects.create(
            name="b2", start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )

        ScoreSummary.objects.create(
            student=cls.student1, batch=cls.batch,
            total_score=Decimal("11.50"), ranking=1,
        )
        ScoreSummary.objects.create(
            student=cls.student2, batch=cls.batch,
            total_score=Decimal("9.00"), ranking=2,
        )

        cls.factory = APIRequestFactory()

    def _get(self, user, params=""):
        request = self.factory.get(f"/api/v1/scores/{params}")
        force_authenticate(request, user=user)
        view = ScoreViewSet.as_view({"get": "list"})
        return view(request)

    # ============================================================
    def test_01_see_own_scores(self):
        response = self._get(self.student1)
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["total_score"], "11.50")
        self.assertEqual(data[0]["ranking"], 1)

    def test_02_cannot_see_others_scores(self):
        response = self._get(self.student1)
        data = response.data["data"]["results"]
        for r in data:
            self.assertEqual(r["student"], self.student1.id)

    def test_03_filter_by_batch(self):
        ScoreSummary.objects.create(
            student=self.student1, batch=self.batch2,
            total_score=Decimal("8.00"), ranking=3,
        )
        response = self._get(self.student1, "?batch=" + str(self.batch2.id))
        data = response.data["data"]["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["total_score"], "8.00")

    def test_04_no_scores_before_summary(self):
        # batch2 has no ScoreSummary for student1 → should not appear
        response = self._get(self.student1)
        data = response.data["data"]["results"]
        ids = [r["batch"] for r in data]
        self.assertNotIn(self.batch2.id, ids)

    def test_05_class_name_present(self):
        response = self._get(self.student1)
        r = response.data["data"]["results"][0]
        self.assertIn("class_name", r)
        self.assertEqual(r["class_name"], "c1")

    def test_06_unauthorized(self):
        request = self.factory.get("/api/v1/scores/")
        view = ScoreViewSet.as_view({"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, 401)
