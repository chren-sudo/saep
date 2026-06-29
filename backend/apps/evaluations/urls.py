"""
evaluations 路由
"""

from rest_framework.routers import DefaultRouter

from .views import EvaluationBatchViewSet

router = DefaultRouter()
router.register(r"batches", EvaluationBatchViewSet, basename="batch")

urlpatterns = router.urls
