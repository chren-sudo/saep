from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "real_name", "email", "phone", "student_no", "student_class", "employee_no", "status", "is_active", "date_joined")
    search_fields = ("username", "real_name", "email", "phone", "student_no", "employee_no")
    list_filter = ("is_active", "status", "is_staff", "student_class", "date_joined")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("扩展信息", {"fields": ("real_name", "phone", "student_no", "employee_no", "student_class", "status")}),
    )
