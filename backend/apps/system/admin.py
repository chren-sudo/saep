from django.contrib import admin

from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "module", "action", "detail", "ip", "created_at")
    search_fields = ("detail", "user__real_name")
    list_filter = ("module", "action", "created_at")
    list_select_related = ("user",)
    readonly_fields = ("user", "module", "action", "detail", "ip", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
