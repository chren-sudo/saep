"""
TASK-043 登录日志 单元测试
"""

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.accounts.roles import add_user_role, ROLE_CHOICES
from apps.accounts.views import login
from apps.system.models import OperationLog
from apps.system.services import get_client_ip, write_operation_log


class LoginLogTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role_name in ROLE_CHOICES:
            Group.objects.get_or_create(name=role_name)

        cls.user = User.objects.create_user(username="ts", password="test123", real_name="测试")
        add_user_role(cls.user, "student")
        cls.factory = APIRequestFactory()

    def _do_login(self, username="ts", password="test123"):
        request = self.factory.post("/api/v1/auth/login/",
            {"username": username, "password": password}, format="json")
        return login(request)

    # ============================================================
    def test_01_login_creates_operation_log(self):
        response = self._do_login()
        self.assertEqual(response.status_code, 200)
        log = OperationLog.objects.get()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.module, "auth")
        self.assertEqual(log.action, "login")

    def test_02_login_failure_no_log(self):
        self._do_login(password="wrong")
        self.assertEqual(OperationLog.objects.count(), 0)

    def test_03_ip_remote_addr(self):
        request = self.factory.post("/", {}, REMOTE_ADDR="10.0.0.1")
        self.assertEqual(get_client_ip(request), "10.0.0.1")

    def test_04_ip_x_forwarded_for(self):
        request = self.factory.post("/", {}, HTTP_X_FORWARDED_FOR="10.0.0.1, 10.0.0.2")
        self.assertEqual(get_client_ip(request), "10.0.0.1")

    def test_05_write_log_failure_does_not_break(self):
        # Simulate DB failure by passing invalid data — should not raise
        try:
            write_operation_log(None, None, "invalid_module", "invalid_action")
        except Exception:
            self.fail("write_operation_log should not raise")
