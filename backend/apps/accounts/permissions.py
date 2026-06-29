"""
accounts 权限类
"""

from rest_framework.permissions import BasePermission


class IsCollegeAdminOrSuperAdmin(BasePermission):
    """院系管理员或系统管理员"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=["college_admin", "super_admin"]
        ).exists()


class IsStudentRole(BasePermission):
    """学生角色"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="student").exists()


class IsCounselorRole(BasePermission):
    """辅导员角色"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="counselor").exists()
