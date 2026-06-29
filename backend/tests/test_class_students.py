"""
TASK-026 ClassStudentViewSet 单元测试
"""

from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.organizations.models import Class, College
from apps.organizations.views import ClassStudentViewSet


class ClassStudentTest(TestCase):
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

        cls.college_admin = User.objects.create_user(username="ca", password="p", real_name="院管")
        add_user_role(cls.college_admin, "college_admin")

        cls.super_admin = User.objects.create_user(username="sa", password="p", real_name="超管")
        add_user_role(cls.super_admin, "super_admin")

        cls.student1 = User.objects.create_user(username="s1", password="p", real_name="学生1",
                                                 student_no="001", phone="111", student_class=cls.class_obj)
        add_user_role(cls.student1, "student")

        cls.student2 = User.objects.create_user(username="s2", password="p", real_name="学生2",
                                                 student_no="002", student_class=cls.class_obj)
        add_user_role(cls.student2, "student")
        add_user_role(cls.student2, "evaluator")

        cls.evaluator = User.objects.create_user(username="ev", password="p", real_name="评审",
                                                  student_class=cls.class_obj)
        add_user_role(cls.evaluator, "evaluator")

        cls.factory = APIRequestFactory()

    def _get(self, user, class_id, params=""):
        request = self.factory.get(f"/api/v1/classes/{class_id}/students/{params}")
        force_authenticate(request, user=user)
        view = ClassStudentViewSet.as_view({"get": "list"})
        return view(request, class_id=class_id)

    # ============================================================
    def test_01_empty_class(self):
        c = Class.objects.create(college=self.college, name="empty", grade="2025")
        c.counselor = self.counselor; c.save()
        response = self._get(self.counselor, c.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_02_with_students(self):
        response = self._get(self.counselor, self.class_obj.id)
        self.assertEqual(response.status_code, 200)
        results = response.data["data"]["results"]
        self.assertTrue(len(results) >= 2)

    def test_03_is_evaluator_flag(self):
        response = self._get(self.counselor, self.class_obj.id)
        results = response.data["data"]["results"]
        s1 = next(r for r in results if r["username"] == "s1")
        s2 = next(r for r in results if r["username"] == "s2")
        self.assertFalse(s1["is_evaluator"])
        self.assertTrue(s2["is_evaluator"])

    def test_04_search_match(self):
        response = self._get(self.counselor, self.class_obj.id, "?search=学生1")
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["real_name"], "学生1")

    def test_05_search_no_result(self):
        response = self._get(self.counselor, self.class_obj.id, "?search=不存在的名字")
        self.assertEqual(len(response.data["data"]["results"]), 0)

    def test_06_pagination(self):
        response = self._get(self.counselor, self.class_obj.id, "?page=1&page_size=1")
        data = response.data["data"]
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["page_size"], 1)

    def test_07_invalid_class_id(self):
        response = self._get(self.counselor, 99999)
        self.assertEqual(response.status_code, 404)

    def test_08_counselor_not_managed(self):
        response = self._get(self.counselor, self.other_class.id)
        self.assertEqual(response.status_code, 404)

    def test_09_counselor_managed(self):
        response = self._get(self.counselor, self.class_obj.id)
        self.assertEqual(response.status_code, 200)

    def test_10_college_admin(self):
        response = self._get(self.college_admin, self.class_obj.id)
        self.assertEqual(response.status_code, 200)

    def test_11_super_admin(self):
        response = self._get(self.super_admin, self.class_obj.id)
        self.assertEqual(response.status_code, 200)

    def test_12_student_forbidden(self):
        response = self._get(self.student1, self.class_obj.id)
        self.assertEqual(response.status_code, 404)

    def test_13_evaluator_forbidden(self):
        response = self._get(self.evaluator, self.class_obj.id)
        self.assertEqual(response.status_code, 404)
