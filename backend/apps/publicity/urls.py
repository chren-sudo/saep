"""
publicity 路由
"""

from rest_framework.routers import DefaultRouter

from .views import PublicNoticeViewSet

router = DefaultRouter()
router.register(r"public-notices", PublicNoticeViewSet, basename="public-notice")

urlpatterns = router.urls
