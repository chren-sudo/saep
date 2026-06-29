"""
TASK-029 PublicNotice 生成公示 单元测试
"""

from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.evaluations.models import EvaluationBatch
from apps.achievements.models import Achievement, AchievementCategory
from apps.accounts.models import User
from apps.publicity.models import PublicNotice
from apps.publicity.views import PublicNoticeViewSet
from rest_framework.exceptions import ValidationError


class PublicNoticeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.college = College.objects.create(code="CS", name="CS")
        cls.class_obj = Class.objects.create(college=cls.college, name="c1", grade="2025")

        cls.counselor = User.objects.create_user(username="tc", password="p", real_name="辅导员")
        add_user_role(cls.counselor, "counselor")
        cls.class_obj.counselor = cls.counselor
        cls.class_obj.save()

        cls.student = User.objects.create_user(username="ts", password="p", real_name="学生",
                                                student_class=cls.class_obj)
        add_user_role(cls.student, "student")

        cls.batch = EvaluationBatch.objects.create(
            name="b", start_time=timezone.now(), end_time=timezone.now()+timezone.timedelta(days=30),
            status=EvaluationBatch.Status.RUNNING,
        )
        cls.category = AchievementCategory.objects.create(name="c")

        # Pre-create approved achievement so create works
        Achievement.objects.create(
            student=cls.student, class_obj=cls.class_obj,
            batch=cls.batch, category=cls.category,
            title="approved", status=Achievement.Status.APPROVED,
        )

        cls.factory = APIRequestFactory()

    def _create(self, user, data):
        request = self.factory.post("/api/v1/public-notices/", data, format="json")
        force_authenticate(request, user=user)
        view = PublicNoticeViewSet.as_view({"post": "create"})
        return view(request)

    def _get(self, user, pk):
        request = self.factory.get(f"/api/v1/public-notices/{pk}/")
        force_authenticate(request, user=user)
        view = PublicNoticeViewSet.as_view({"get": "retrieve"})
        return view(request, pk=pk)

    def _make_data(self, **kw):
        data = {
            "batch": self.batch.id,
            "class_obj": self.class_obj.id,
            "title": "公示",
            "start_time": "2026-07-01T00:00:00Z",
            "end_time": "2026-07-10T00:00:00Z",
        }
        data.update(kw)
        return data

    # ============================================================
    def test_01_create_success(self):
        response = self._create(self.counselor, self._make_data())
        self.assertEqual(response.status_code, 201)

    def test_02_duplicate_rejected(self):
        self._create(self.counselor, self._make_data())
        response = self._create(self.counselor, self._make_data())
        self.assertEqual(response.status_code, 400)

    def test_03_not_counselor(self):
        response = self._create(self.student, self._make_data())
        self.assertEqual(response.status_code, 403)

    def test_04_start_gte_end(self):
        response = self._create(self.counselor,
            self._make_data(start_time="2026-07-10T00:00:00Z", end_time="2026-07-01T00:00:00Z"))
        self.assertEqual(response.status_code, 400)

    def test_05_no_approved_achievements(self):
        empty = Class.objects.create(college=self.college, name="empty", grade="2025")
        empty.counselor = self.counselor; empty.save()
        response = self._create(self.counselor, self._make_data(class_obj=empty.id))
        self.assertEqual(response.status_code, 400)

    def test_06_approved_count(self):
        Achievement.objects.create(
            student=self.student, class_obj=self.class_obj,
            batch=self.batch, category=self.category,
            title="a2", status=Achievement.Status.APPROVED,
        )
        self._create(self.counselor, self._make_data())
        # Get via list
        request = self.factory.get("/api/v1/public-notices/")
        force_authenticate(request, user=self.counselor)
        view = PublicNoticeViewSet.as_view({"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        results = response.data["data"]["results"]
        self.assertTrue(len(results) > 0)
        self.assertIn("approved_count", results[0])

    def test_07_unique_constraint_db_level(self):
        self._create(self.counselor, self._make_data())
        with self.assertRaises(IntegrityError):
            PublicNotice.objects.create(
                batch=self.batch, class_obj=self.class_obj,
                title="绕过", start_time=timezone.now(), end_time=timezone.now(),
            )

    # ============================================================
    # TASK-030: publish
    # ============================================================

    def _publish(self, user, pk):
        request = self.factory.post(f"/api/v1/public-notices/{pk}/publish/")
        force_authenticate(request, user=user)
        view = PublicNoticeViewSet.as_view({"post": "publish"})
        return view(request, pk=pk)

    def test_08_publish_success(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        response = self._publish(self.counselor, n.id)
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertEqual(n.status, PublicNotice.Status.PUBLISHED)

    def test_09_publish_twice_rejected(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        self._publish(self.counselor, n.id)
        response = self._publish(self.counselor, n.id)
        self.assertEqual(response.status_code, 400)

    def test_10_publish_not_counselor(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        response = self._publish(self.student, n.id)
        self.assertEqual(response.status_code, 403)

    def test_11_check_notice_status_helper(self):
        n = PublicNotice.objects.create(
            batch=self.batch, class_obj=self.class_obj,
            title="x", start_time=timezone.now(), end_time=timezone.now(),
            status=PublicNotice.Status.PUBLISHED,
        )
        view = PublicNoticeViewSet()
        with self.assertRaises(ValidationError):
            view._check_notice_status(n, PublicNotice.Status.DRAFT)

    # ============================================================
    # TASK-031: close
    # ============================================================

    def _close(self, user, pk):
        request = self.factory.post(f"/api/v1/public-notices/{pk}/close/")
        force_authenticate(request, user=user)
        view = PublicNoticeViewSet.as_view({"post": "close"})
        return view(request, pk=pk)

    def test_12_close_success(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        n.status = PublicNotice.Status.PUBLISHED; n.save()
        response = self._close(self.counselor, n.id)
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertEqual(n.status, PublicNotice.Status.CLOSED)

    def test_13_close_twice_rejected(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        n.status = PublicNotice.Status.PUBLISHED; n.save()
        self._close(self.counselor, n.id)
        response = self._close(self.counselor, n.id)
        self.assertEqual(response.status_code, 400)

    def test_14_close_draft_rejected(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        response = self._close(self.counselor, n.id)
        self.assertEqual(response.status_code, 400)

    def test_15_close_not_counselor(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        response = self._close(self.student, n.id)
        self.assertEqual(response.status_code, 403)

    def test_16_close_not_managed_class(self):
        data = self._make_data()
        self._create(self.counselor, data)
        n = PublicNotice.objects.get(batch=self.batch, class_obj=self.class_obj)
        n.status = PublicNotice.Status.PUBLISHED; n.save()
        # Create another counselor who doesn't manage this class
        other_counselor = User.objects.create_user(username="oc", password="p", real_name="其他辅导员")
        add_user_role(other_counselor, "counselor")
        response = self._close(other_counselor, n.id)
        self.assertEqual(response.status_code, 404)
