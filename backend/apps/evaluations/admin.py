from django.contrib import admin

from .models import EvaluationBatch


@admin.register(EvaluationBatch)
class EvaluationBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "start_time", "end_time", "created_at")
    search_fields = ("name", "description")
    list_filter = ("status",)
