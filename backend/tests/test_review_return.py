"""
TASK-022 Return 审核退回单元测试
"""

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


class ReturnTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")
        cls.other_class = Class.objects.create(college=cls.college, name="c2", grade="2025")

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

    def _make(self, status, class_obj=None):
        return Achievement.objects.create(
            student=self.student, class_obj=class_obj or self.class_obj,
            batch=self.batch, category=self.category,
            title=f"t-{status}", status=status,
        )

    def _do_return(self, user, ach_id, data=None):
        if data is None:
            data = {"comment": "需要修改"}
        request = self.factory.post(f"/api/v1/reviews/{ach_id}/return/", data, format="json")
        force_authenticate(request, user=user)
        view = ReviewViewSet.as_view({"post": "return_achievement"})
        return view(request, pk=ach_id)

    def test_01_evaluator_return_to_draft(self):
        a = self._make(Achievement.Status.SUBMITTED)
        response = self._do_return(self.evaluator, a.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["status"], "draft")
        a.refresh_from_db()
        self.assertEqual(a.status, "draft")
        rec = AuditRecord.objects.get(achievement=a)
        self.assertEqual(rec.review_stage, "evaluator")
        self.assertEqual(rec.action, "return")
        self.assertIsNone(rec.score)

    def test_02_counselor_return_to_draft(self):
        a = self._make(Achievement.Status.COUNSELOR_REVIEWING)
        response = self._do_return(self.counselor, a.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["status"], "draft")
        a.refresh_from_db()
        self.assertEqual(a.status, "draft")

    def test_03_comment_required(self):
        a = self._make(Achievement.Status.SUBMITTED)
        request = self.factory.post(f"/api/v1/reviews/{a.id}/return/", {}, format="json")
        force_authenticate(request, user=self.evaluator)
        view = ReviewViewSet.as_view({"post": "return_achievement"})
        response = view(request, pk=a.id)
        self.assertEqual(response.status_code, 400)

    def test_04_score_unchanged(self):
        a = self._make(Achievement.Status.COUNSELOR_REVIEWING)
        a.score = 9.0
        a.save()
        self._do_return(self.counselor, a.id)
        a.refresh_from_db()
        self.assertEqual(a.score, 9.0)

    def test_05_student_not_in_scope(self):
        a = self._make(Achievement.Status.SUBMITTED)
        response = self._do_return(self.student, a.id)
        self.assertEqual(response.status_code, 404)

    def test_06_wrong_status_not_found(self):
        a = self._make(Achievement.Status.APPROVED)
        response = self._do_return(self.counselor, a.id)
        self.assertEqual(response.status_code, 404)
