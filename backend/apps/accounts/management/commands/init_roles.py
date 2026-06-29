"""
初始化角色命令

创建 5 个 Django Group：
    student / evaluator / counselor / college_admin / super_admin

用法：
    python manage.py init_roles
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

ROLES = {
    "student": {
        "verbose_name": "学生",
        "permissions": [],
    },
    "evaluator": {
        "verbose_name": "测评小组成员",
        "permissions": [],
    },
    "counselor": {
        "verbose_name": "辅导员",
        "permissions": [],
    },
    "college_admin": {
        "verbose_name": "院系管理员",
        "permissions": [],
    },
    "super_admin": {
        "verbose_name": "系统管理员",
        "permissions": [],
    },
}


class Command(BaseCommand):
    help = "初始化系统角色（5 个 Group）"

    def handle(self, *args, **options):
        created_count = 0
        for role_name, config in ROLES.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + 创建角色: {role_name} ({config['verbose_name']})"))
            else:
                self.stdout.write(f"    角色已存在: {role_name} ({config['verbose_name']})")

        self.stdout.write("")
        total = Group.objects.filter(name__in=ROLES.keys()).count()
        self.stdout.write(self.style.SUCCESS(f"角色初始化完成: {total}/5"))
