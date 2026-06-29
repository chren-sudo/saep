"""
角色工具函数

角色绑定/解绑操作，基于 Django Group。
"""

from django.contrib.auth.models import Group

ROLE_CHOICES = [
    "student",
    "evaluator",
    "counselor",
    "college_admin",
    "super_admin",
]


def set_user_role(user, role_name):
    """为用户设置单个角色（替换所有已有角色）

    Args:
        user: User 实例
        role_name: 角色名（如 "student"）
    """
    if role_name not in ROLE_CHOICES:
        raise ValueError(f"无效角色: {role_name}，可选值: {ROLE_CHOICES}")

    group = Group.objects.get(name=role_name)
    user.groups.set([group])


def add_user_role(user, role_name):
    """为用户追加角色（保留已有角色）

    Args:
        user: User 实例
        role_name: 角色名
    """
    if role_name not in ROLE_CHOICES:
        raise ValueError(f"无效角色: {role_name}，可选值: {ROLE_CHOICES}")

    group = Group.objects.get(name=role_name)
    user.groups.add(group)


def remove_user_role(user, role_name):
    """移除用户的某个角色

    Args:
        user: User 实例
        role_name: 角色名
    """
    if role_name not in ROLE_CHOICES:
        raise ValueError(f"无效角色: {role_name}，可选值: {ROLE_CHOICES}")

    group = Group.objects.get(name=role_name)
    user.groups.remove(group)


def get_user_roles(user):
    """获取用户的所有角色名

    Returns:
        list[str]: 角色名列表，如 ["student"]
    """
    return list(user.groups.values_list("name", flat=True))
