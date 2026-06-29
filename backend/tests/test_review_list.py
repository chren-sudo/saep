"""
TASK-020 ReviewViewSet 单元测试
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth.models import Group
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.achievements.models import Achievement, AchievementCategory
from apps.achievements.views import ReviewViewSet
from apps.evaluations.models import EvaluationBatch
from apps.organizations.models import Class, College


class ReviewViewSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Initialize roles first
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="计算机学院")
        cls.class_obj = Class.objects.create(
            college=cls.college, name="计算机1班", grade="2025级"
        )
        cls.other_class = Class.objects.create(
            college=cls.college, name="计算机2班", grade="2025级"
        )

        # Evaluator (学生 + evaluator 角色)
        cls.evaluator = User.objects.create_user(
            username="test_evaluator", password="test123",
            real_name="评审员", student_class=cls.class_obj,
        )
        add_user_role(cls.evaluator, "evaluator")

        # Counselor
        cls.counselor = User.objects.create_user(
            username="test_counselor", password="test123",
            real_name="辅导员",
        )
        add_user_role(cls.counselor, "counselor")
        cls.class_obj.counselor = cls.counselor
        cls.class_obj.save()

        # Student
        cls.student = User.objects.create_user(
            username="test_student", password="test123",
            real_name="学生", student_class=cls.class_obj,
        )
        add_user_role(cls.student, "student")

        # Batch
        cls.batch = EvaluationBatch.objects.create(
            name="测试批次",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="测试分类")

        # Submitted achievement (evaluator 应可见)
        cls.submitted = Achievement.objects.create(
            student=cls.student, class_obj=cls.class_obj,
            batch=cls.batch, category=cls.category,
            title="待审核成果", status=Achievement.Status.SUBMITTED,
        )
        # Counselor_reviewing (counselor 应可见)
        cls.counselor_reviewing = Achievement.objects.create(
            student=cls.student, class_obj=cls.class_obj,
            batch=cls.batch, category=cls.category,
            title="待终审成果", status=Achievement.Status.COUNSELOR_REVIEWING,
        )
        # Other class submitted (evaluator 不应可见)
        cls.other = Achievement.objects.create(
            student=cls.student, class_obj=cls.other_class,
            batch=cls.batch, category=cls.category,
            title="他班成果", status=Achievement.Status.SUBMITTED,
        )

        cls.factory = APIRequestFactory()

    # ============================================================
    # Test 1: Evaluator 只能看到本班 submitted
    # ============================================================
    def test_01_evaluator_sees_class_submitted(self):
        request = self.factory.get("/api/v1/reviews/")
        force_authenticate(request, user=self.evaluator)
        view = ReviewViewSet.as_view({"get": "list"})
        response = view(request)
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["title"], "待审核成果")

    # ============================================================
    # Test 2: Counselor 只能看到本班 counselor_reviewing
    # ============================================================
    def test_02_counselor_sees_class_counselor_reviewing(self):
        request = self.factory.get("/api/v1/reviews/")
        force_authenticate(request, user=self.counselor)
        view = ReviewViewSet.as_view({"get": "list"})
        response = view(request)
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["title"], "待终审成果")

    # ============================================================
    # Test 3: Student 不应看到待审核列表
    # ============================================================
    def test_03_student_sees_nothing(self):
        request = self.factory.get("/api/v1/reviews/")
        force_authenticate(request, user=self.student)
        view = ReviewViewSet.as_view({"get": "list"})
        response = view(request)
        data = response.data["data"]
        self.assertEqual(data["total"], 0)

    # ============================================================
    # Test 4: has_attachment 字段存在
    # ============================================================
    def test_04_has_attachment_field(self):
        request = self.factory.get("/api/v1/reviews/")
        force_authenticate(request, user=self.evaluator)
        view = ReviewViewSet.as_view({"get": "list"})
        response = view(request)
        result = response.data["data"]["results"][0]
        self.assertIn("has_attachment", result)
        self.assertFalse(result["has_attachment"])

    # ============================================================
    # Test 5: ReviewViewSet 仅包含 ListModelMixin（无 retrieve/create/update/destroy）
    # ============================================================
    def test_05_no_create_update_destroy(self):
        from rest_framework.mixins import ListModelMixin
        self.assertTrue(issubclass(ReviewViewSet, ListModelMixin))

        # 验证没有 ModelViewSet 的额外 mixins
        from rest_framework.mixins import (
            CreateModelMixin,
            DestroyModelMixin,
            RetrieveModelMixin,
            UpdateModelMixin,
        )
        self.assertFalse(issubclass(ReviewViewSet, CreateModelMixin))
        self.assertFalse(issubclass(ReviewViewSet, RetrieveModelMixin))
        self.assertFalse(issubclass(ReviewViewSet, UpdateModelMixin))
        self.assertFalse(issubclass(ReviewViewSet, DestroyModelMixin))
