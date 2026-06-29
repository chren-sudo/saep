from django.contrib import admin

from .models import ScoreSummary


@admin.register(ScoreSummary)
class ScoreSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "batch", "total_score", "ranking", "created_at")
    search_fields = ("student__real_name", "student__student_no")
    list_filter = ("batch",)
    list_select_related = ("student", "batch")
    readonly_fields = ("student", "batch", "total_score", "ranking",
                       "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
