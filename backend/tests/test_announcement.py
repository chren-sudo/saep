"""
TASK-038 Announcement 通知发布 单元测试
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.notifications.models import Announcement
from apps.notifications.views import AnnouncementViewSet


class AnnouncementTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.super_admin = User.objects.create_user(username="sa", password="p", real_name="超管")
        add_user_role(cls.super_admin, "super_admin")

        cls.college_admin = User.objects.create_user(username="ca", password="p", real_name="院管")
        add_user_role(cls.college_admin, "college_admin")

        cls.counselor = User.objects.create_user(username="tc", password="p", real_name="辅导员")
        add_user_role(cls.counselor, "counselor")

        cls.student = User.objects.create_user(username="ts", password="p", real_name="学生")
        add_user_role(cls.student, "student")

        cls.factory = APIRequestFactory()

    def _create(self, user, data=None):
        if data is None:
            data = {"title": "通知", "content": "内容"}
        request = self.factory.post("/api/v1/announcements/", data, format="json")
        force_authenticate(request, user=user)
        view = AnnouncementViewSet.as_view({"post": "create"})
        return view(request)

    def _list(self, user):
        request = self.factory.get("/api/v1/announcements/")
        force_authenticate(request, user=user)
        view = AnnouncementViewSet.as_view({"get": "list"})
        return view(request)

    # ============================================================
    def test_01_super_admin_can_create(self):
        response = self._create(self.super_admin)
        self.assertEqual(response.status_code, 201)
        a = Announcement.objects.get()
        self.assertEqual(a.publisher, self.super_admin)
        self.assertEqual(a.title, "通知")

    def test_02_college_admin_can_create(self):
        response = self._create(self.college_admin)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Announcement.objects.get().publisher, self.college_admin)

    def test_03_counselor_forbidden(self):
        response = self._create(self.counselor)
        self.assertEqual(response.status_code, 403)

    def test_04_student_forbidden(self):
        response = self._create(self.student)
        self.assertEqual(response.status_code, 403)

    def test_05_title_required(self):
        response = self._create(self.super_admin, {"content": "内容"})
        self.assertEqual(response.status_code, 400)

    def test_06_content_required(self):
        response = self._create(self.super_admin, {"title": "标题"})
        self.assertEqual(response.status_code, 400)

    def test_07_list_all_roles(self):
        self._create(self.super_admin)
        response = self._list(self.student)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assertIn("publisher_name", response.data["data"]["results"][0])

    def test_08_no_update_destroy_routes(self):
        from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
        self.assertFalse(issubclass(AnnouncementViewSet, UpdateModelMixin))
        self.assertFalse(issubclass(AnnouncementViewSet, DestroyModelMixin))

    def test_09_publisher_readonly(self):
        response = self._create(self.super_admin, {"title": "t", "content": "c", "publisher": 999})
        if response.status_code == 201:
            a = Announcement.objects.get()
            self.assertEqual(a.publisher, self.super_admin)
