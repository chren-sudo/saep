from django.contrib import admin

from .models import Class, College


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "created_at")
    search_fields = ("name", "code")
    ordering = ("code",)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "college", "grade", "counselor", "created_at")
    search_fields = ("name", "college__name")
    list_filter = ("college", "grade")
    list_select_related = ("college", "counselor")
    autocomplete_fields = ("college", "counselor")
