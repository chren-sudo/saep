"""
statistics 路由
"""

from rest_framework.routers import DefaultRouter

from .views import ExportViewSet, ScoreViewSet

router = DefaultRouter()
router.register(r"scores", ScoreViewSet, basename="score")
router.register(r"export", ExportViewSet, basename="export")

urlpatterns = router.urls
