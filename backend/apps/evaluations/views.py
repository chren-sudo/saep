"""
evaluations 视图
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsCollegeAdminOrSuperAdmin

from .models import EvaluationBatch
from .serializers import EvaluationBatchSerializer, EvaluationBatchWriteSerializer


class EvaluationBatchViewSet(ModelViewSet):
    """测评批次 CRUD"""

    queryset = EvaluationBatch.objects.all()
    filterset_fields = ["status"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "start_time"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsCollegeAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EvaluationBatchWriteSerializer
        return EvaluationBatchSerializer
