"""
Hotfix: Submit 提交审核 单元测试
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.evaluations.models import EvaluationBatch
from apps.achievements.models import Achievement, AchievementCategory
from apps.achievements.views import AchievementViewSet


class SubmitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")

        cls.student = User.objects.create_user(username="s1", password="p", real_name="张三",
                                                student_class=cls.class_obj)
        add_user_role(cls.student, "student")

        cls.other = User.objects.create_user(username="s2", password="p", real_name="李四",
                                              student_class=cls.class_obj)
        add_user_role(cls.other, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="c")
        cls.factory = APIRequestFactory()

    def _submit(self, user, aid):
        request = self.factory.post(f"/api/v1/achievements/{aid}/submit/")
        force_authenticate(request, user=user)
        view = AchievementViewSet.as_view({"post": "submit"})
        return view(request, pk=aid)

    def _make(self, student, status="draft"):
        return Achievement.objects.create(
            student=student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title="t", status=status,
        )

    def test_01_draft_submit_success(self):
        a = self._make(self.student)
        response = self._submit(self.student, a.id)
        self.assertEqual(response.status_code, 200)
        a.refresh_from_db()
        self.assertEqual(a.status, "submitted")
        self.assertIsNotNone(a.submitted_at)

    def test_02_duplicate_submit_rejected(self):
        a = self._make(self.student)
        self._submit(self.student, a.id)
        response = self._submit(self.student, a.id)
        self.assertEqual(response.status_code, 400)

    def test_03_not_owner_not_found(self):
        a = self._make(self.student)
        response = self._submit(self.other, a.id)
        self.assertEqual(response.status_code, 404)

    def test_04_submitted_at_written(self):
        a = self._make(self.student)
        self.assertIsNone(a.submitted_at)
        self._submit(self.student, a.id)
        a.refresh_from_db()
        self.assertIsNotNone(a.submitted_at)
