"""
TASK-036 班级排名 单元测试
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


class RankingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")
        cls.other_class = Class.objects.create(college=cls.college, name="c2", grade="2025")

        cls.counselor = User.objects.create_user(username="tc", password="p", real_name="辅导员")
        add_user_role(cls.counselor, "counselor")
        cls.class_obj.counselor = cls.counselor
        cls.class_obj.save()

        cls.super_admin = User.objects.create_user(username="sa", password="p", real_name="超管")
        add_user_role(cls.super_admin, "super_admin")

        cls.student = User.objects.create_user(username="s1", password="p", real_name="学生",
                                                student_class=cls.class_obj, student_no="001")
        add_user_role(cls.student, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )

        # Pre-ranked data
        ScoreSummary.objects.create(student=cls.student, batch=cls.batch,
                                     total_score=Decimal("10.0"), ranking=1)

        cls.factory = APIRequestFactory()

    def _ranking(self, user, params=""):
        request = self.factory.get(f"/api/v1/scores/ranking/{params}")
        force_authenticate(request, user=user)
        view = ScoreViewSet.as_view({"get": "ranking"})
        return view(request)

    # ============================================================
    def test_01_ranking_returns_data(self):
        response = self._ranking(self.super_admin, "?batch=" + str(self.batch.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)

    def test_02_batch_required(self):
        response = self._ranking(self.super_admin, "")
        self.assertEqual(response.status_code, 400)

    def test_03_skips_no_ranking(self):
        # Create unranked student (ranking=0 should be excluded)
        u2 = User.objects.create_user(username="s2", password="p", real_name="学生2",
                                       student_class=self.class_obj, student_no="002")
        add_user_role(u2, "student")
        ScoreSummary.objects.create(student=u2, batch=self.batch,
                                     total_score=Decimal("3.0"), ranking=0)
        response = self._ranking(self.super_admin, "?batch=" + str(self.batch.id))
        results = response.data["data"]["results"]
        # only s1 (ranking=1) returned, s2 (ranking=0) excluded
        self.assertEqual(len(results), 1)

    def test_04_sorted_by_ranking_asc(self):
        u2 = User.objects.create_user(username="s2", password="p", real_name="学生2",
                                       student_class=self.class_obj, student_no="002")
        add_user_role(u2, "student")
        ScoreSummary.objects.create(student=u2, batch=self.batch,
                                     total_score=Decimal("5.0"), ranking=2)
        response = self._ranking(self.super_admin, "?batch=" + str(self.batch.id))
        results = response.data["data"]["results"]
        self.assertLessEqual(results[0]["ranking"], results[-1]["ranking"])

    def test_05_counselor_only_managed_class(self):
        response = self._ranking(
            self.counselor,
            f"?batch={self.batch.id}&class_id={self.class_obj.id}"
        )
        self.assertEqual(response.status_code, 200)

    def test_06_counselor_cannot_query_other_class(self):
        response = self._ranking(
            self.counselor,
            f"?batch={self.batch.id}&class_id={self.other_class.id}"
        )
        self.assertEqual(response.status_code, 404)

    def test_07_student_only_own(self):
        response = self._ranking(self.student, "?batch=" + str(self.batch.id))
        self.assertEqual(response.status_code, 200)
        results = response.data["data"]["results"]
        for r in results:
            self.assertEqual(r["student"], self.student.id)

    def test_08_unauthorized(self):
        request = self.factory.get(f"/api/v1/scores/ranking/?batch={self.batch.id}")
        view = ScoreViewSet.as_view({"get": "ranking"})
        response = view(request)
        self.assertEqual(response.status_code, 401)
