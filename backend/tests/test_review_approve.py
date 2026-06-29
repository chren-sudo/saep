"""
TASK-021 Approve 审核通过单元测试
"""

from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.achievements.models import Achievement, AchievementCategory, AuditRecord
from apps.achievements.views import ReviewViewSet
from apps.evaluations.models import EvaluationBatch
from apps.organizations.models import Class, College
from django.utils import timezone


class ApproveTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="计算机学院")
        cls.class_obj = Class.objects.create(college=cls.college, name="计算机1班", grade="2025级")
        cls.other_class = Class.objects.create(college=cls.college, name="计算机2班", grade="2025级")

        cls.evaluator = User.objects.create_user(username="te", password="p", real_name="评审员", student_class=cls.class_obj)
        add_user_role(cls.evaluator, "evaluator")

        cls.counselor = User.objects.create_user(username="tc", password="p", real_name="辅导员")
        add_user_role(cls.counselor, "counselor")
        cls.class_obj.counselor = cls.counselor
        cls.class_obj.save()

        cls.student = User.objects.create_user(username="ts", password="p", real_name="学生", student_class=cls.class_obj)
        add_user_role(cls.student, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(), end_time=timezone.now()+timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="c")

        cls.factory = APIRequestFactory()

    def _make_achievement(self, status, class_obj=None, student=None):
        return Achievement.objects.create(
            student=student or self.student,
            class_obj=class_obj or self.class_obj,
            batch=self.batch, category=self.category,
            title=f"test-{status}", status=status,
        )

    def _approve(self, user, achievement_id, data=None):
        if data is None:
            data = {"score": "8.00"}
        request = self.factory.post(f"/api/v1/reviews/{achievement_id}/approve/", data, format="json")
        force_authenticate(request, user=user)
        view = ReviewViewSet.as_view({"post": "approve"})
        return view(request, pk=achievement_id)

    # ============================================================
    # Test 1: Evaluator approve submitted → counselor_reviewing
    # ============================================================
    def test_01_evaluator_approve_success(self):
        a = self._make_achievement(Achievement.Status.SUBMITTED)
        response = self._approve(self.evaluator, a.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["status"], "counselor_reviewing")

        a.refresh_from_db()
        self.assertEqual(a.status, "counselor_reviewing")
        self.assertEqual(a.score, Decimal("8.00"))

        rec = AuditRecord.objects.get(achievement=a)
        self.assertEqual(rec.review_stage, "evaluator")
        self.assertEqual(rec.score, Decimal("8.00"))
        self.assertEqual(rec.reviewer_name, "评审员")

    # ============================================================
    # Test 2: Counselor approve counselor_reviewing → approved
    # ============================================================
    def test_02_counselor_approve_success(self):
        a = self._make_achievement(Achievement.Status.COUNSELOR_REVIEWING)
        response = self._approve(self.counselor, a.id, {"score": "9.00"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["status"], "approved")

        a.refresh_from_db()
        self.assertEqual(a.status, "approved")
        self.assertEqual(a.score, Decimal("9.00"))

        rec = AuditRecord.objects.get(achievement=a)
        self.assertEqual(rec.review_stage, "counselor")
        self.assertEqual(rec.reviewer_name, "辅导员")

    # ============================================================
    # Test 3: Wrong status → 404 (get_queryset filters out)
    # ============================================================
    def test_03_wrong_status_not_found(self):
        a = self._make_achievement(Achievement.Status.APPROVED)
        response = self._approve(self.counselor, a.id)
        self.assertEqual(response.status_code, 404)

    # ============================================================
    # Test 4: Missing score → 400
    # ============================================================
    def test_04_missing_score(self):
        a = self._make_achievement(Achievement.Status.SUBMITTED)
        request = self.factory.post(f"/api/v1/reviews/{a.id}/approve/", {}, format="json")
        force_authenticate(request, user=self.evaluator)
        view = ReviewViewSet.as_view({"post": "approve"})
        response = view(request, pk=a.id)
        self.assertEqual(response.status_code, 400)

    # ============================================================
    # Test 5: Student role → 404 (get_queryset returns qs.none())
    # ============================================================
    def test_05_student_not_in_scope(self):
        a = self._make_achievement(Achievement.Status.SUBMITTED)
        response = self._approve(self.student, a.id)
        self.assertEqual(response.status_code, 404)

    # ============================================================
    # Test 6: Other class → 404 (get_queryset filters by class_obj)
    # ============================================================
    def test_06_other_class_not_found(self):
        a = self._make_achievement(Achievement.Status.SUBMITTED, class_obj=self.other_class)
        response = self._approve(self.evaluator, a.id)
        self.assertEqual(response.status_code, 404)

    # ============================================================
    # Test 7: transaction.atomic + AuditRecord created
    # ============================================================
    def test_07_audit_record_created(self):
        a = self._make_achievement(Achievement.Status.SUBMITTED)
        self._approve(self.evaluator, a.id)
        self.assertEqual(AuditRecord.objects.filter(achievement=a).count(), 1)
        rec = AuditRecord.objects.get(achievement=a)
        self.assertEqual(rec.action, "approve")
        self.assertEqual(rec.score, Decimal("8.00"))
