"""
TASK-025 Evaluator Management 单元测试
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.organizations.views import EvaluatorViewSet


class EvaluatorTest(TestCase):
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

        cls.student = User.objects.create_user(username="ts", password="p", real_name="学生",
                                                student_class=cls.class_obj)
        add_user_role(cls.student, "student")

        cls.student2 = User.objects.create_user(username="ts2", password="p", real_name="学生2",
                                                 student_class=cls.other_class)
        add_user_role(cls.student2, "student")

        cls.factory = APIRequestFactory()

    def _get(self, user, class_id):
        request = self.factory.get(f"/api/v1/classes/{class_id}/evaluators/")
        force_authenticate(request, user=user)
        view = EvaluatorViewSet.as_view({"get": "list"})
        return view(request, class_id=class_id)

    def _post(self, user, class_id, data):
        request = self.factory.post(f"/api/v1/classes/{class_id}/evaluators/", data, format="json")
        force_authenticate(request, user=user)
        view = EvaluatorViewSet.as_view({"post": "create"})
        return view(request, class_id=class_id)

    def _delete(self, user, class_id, pk):
        request = self.factory.delete(f"/api/v1/classes/{class_id}/evaluators/{pk}/")
        force_authenticate(request, user=user)
        view = EvaluatorViewSet.as_view({"delete": "destroy"})
        return view(request, class_id=class_id, pk=pk)

    # ============================================================
    def test_01_list_empty(self):
        response = self._get(self.counselor, self.class_obj.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 0)

    def test_02_add_success(self):
        response = self._post(self.counselor, self.class_obj.id, {"user_id": self.student.id})
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertTrue(self.student.groups.filter(name="evaluator").exists())

    def test_03_list_after_add(self):
        self._post(self.counselor, self.class_obj.id, {"user_id": self.student.id})
        response = self._get(self.counselor, self.class_obj.id)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["real_name"], "学生")

    def test_04_duplicate_idempotent(self):
        self._post(self.counselor, self.class_obj.id, {"user_id": self.student.id})
        response = self._post(self.counselor, self.class_obj.id, {"user_id": self.student.id})
        self.assertEqual(response.status_code, 200)

    def test_05_delete_success(self):
        self._post(self.counselor, self.class_obj.id, {"user_id": self.student.id})
        response = self._delete(self.counselor, self.class_obj.id, self.student.id)
        self.assertEqual(response.status_code, 204)
        self.student.refresh_from_db()
        self.assertFalse(self.student.groups.filter(name="evaluator").exists())
        self.assertTrue(self.student.groups.filter(name="student").exists())

    def test_06_student_not_in_class(self):
        response = self._post(self.counselor, self.class_obj.id, {"user_id": self.student2.id})
        self.assertEqual(response.status_code, 400)

    def test_07_not_counselor(self):
        response = self._get(self.student, self.class_obj.id)
        self.assertEqual(response.status_code, 404)

    def test_08_wrong_class(self):
        other = Class.objects.create(college=self.college, name="c3", grade="2025")
        response = self._get(self.counselor, other.id)
        self.assertEqual(response.status_code, 404)

    def test_09_delete_not_evaluator(self):
        response = self._delete(self.counselor, self.class_obj.id, self.student.id)
        self.assertEqual(response.status_code, 400)

    def test_10_delete_nonexistent_user(self):
        response = self._delete(self.counselor, self.class_obj.id, 99999)
        self.assertEqual(response.status_code, 404)
