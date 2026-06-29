from django.contrib import admin

from .models import Achievement, AchievementCategory, AuditRecord


@admin.register(AchievementCategory)
class AchievementCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sort_order", "created_at")
    search_fields = ("name",)
    ordering = ("sort_order", "id")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "student", "class_obj", "batch", "category",
                    "status", "score", "achievement_date", "created_at")
    search_fields = ("title", "student__real_name", "student__student_no")
    list_filter = ("status", "batch", "category", "class_obj")
    list_select_related = ("student", "class_obj", "batch", "category")
    autocomplete_fields = ("student", "class_obj", "batch", "category")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AuditRecord)
class AuditRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "achievement", "review_stage", "action",
                    "reviewer_name", "score", "created_at")
    search_fields = ("achievement__title", "reviewer_name", "reviewer__real_name")
    list_filter = ("review_stage", "action")
    list_select_related = ("achievement", "reviewer")
    readonly_fields = ("achievement", "reviewer", "reviewer_name",
                       "review_stage", "action", "score", "comment",
                       "created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
