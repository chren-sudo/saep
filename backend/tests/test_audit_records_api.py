"""
TASK-024 Audit Records API 单元测试
"""

from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.achievements.models import Achievement, AchievementCategory, AuditRecord
from apps.achievements.views import AchievementViewSet
from apps.evaluations.models import EvaluationBatch
from apps.organizations.models import Class, College
from django.utils import timezone


class AuditRecordsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")
        cls.student = User.objects.create_user(username="ts", password="p", real_name="学生", student_class=cls.class_obj)
        add_user_role(cls.student, "student")
        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(), end_time=timezone.now()+timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="c")
        cls.factory = APIRequestFactory()

    def _make_achievement(self, status="draft"):
        return Achievement.objects.create(
            student=self.student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title="t", status=status,
        )

    def _get_audit_records(self, user, achievement_id):
        request = self.factory.get(f"/api/v1/achievements/{achievement_id}/audit-records/")
        force_authenticate(request, user=user)
        view = AchievementViewSet.as_view({"get": "audit_records"})
        return view(request, pk=achievement_id)

    # ============================================================
    def test_01_returns_audit_records(self):
        a = self._make_achievement()
        AuditRecord.objects.create(
            achievement=a, reviewer=self.student, reviewer_name="张三",
            review_stage="evaluator", action="approve", score=Decimal("8.00"),
        )
        AuditRecord.objects.create(
            achievement=a, reviewer=self.student, reviewer_name="李四",
            review_stage="counselor", action="approve", score=Decimal("9.00"),
        )
        response = self._get_audit_records(self.student, a.id)
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(len(data), 2)
        # 升序 — 第一条是 evaluator
        self.assertEqual(data[0]["review_stage"], "evaluator")
        self.assertEqual(data[1]["review_stage"], "counselor")

    def test_02_empty_audit_records(self):
        a = self._make_achievement()
        response = self._get_audit_records(self.student, a.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 0)

    def test_03_achievement_not_found(self):
        response = self._get_audit_records(self.student, 99999)
        self.assertEqual(response.status_code, 404)

    def test_04_unauthorized(self):
        a = self._make_achievement()
        request = self.factory.get(f"/api/v1/achievements/{a.id}/audit-records/")
        view = AchievementViewSet.as_view({"get": "audit_records"})
        response = view(request, pk=a.id)
        self.assertEqual(response.status_code, 401)

    def test_05_fields_present(self):
        a = self._make_achievement()
        AuditRecord.objects.create(
            achievement=a, reviewer=self.student, reviewer_name="测试",
            review_stage="evaluator", action="return",
        )
        response = self._get_audit_records(self.student, a.id)
        rec = response.data["data"][0]
        self.assertIn("review_stage_display", rec)
        self.assertIn("action_display", rec)
        self.assertIn("reviewer_name", rec)
        self.assertIn("score", rec)
        self.assertIn("comment", rec)
        self.assertIn("created_at", rec)
        # reviewer 不在 serializer 中
        self.assertNotIn("reviewer", rec)
