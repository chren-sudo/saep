from django.contrib import admin

from .models import PublicNotice


@admin.register(PublicNotice)
class PublicNoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "batch", "class_obj", "status",
                    "start_time", "end_time", "created_at")
    search_fields = ("title",)
    list_filter = ("status", "batch")
    list_select_related = ("batch", "class_obj")
