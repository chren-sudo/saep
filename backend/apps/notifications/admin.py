from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "publisher", "created_at")
    search_fields = ("title", "content")
    list_select_related = ("publisher",)
    readonly_fields = ("publisher", "created_at", "updated_at")
