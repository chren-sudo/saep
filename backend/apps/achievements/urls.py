"""
achievements 路由
"""

from rest_framework.routers import DefaultRouter

from .views import AchievementCategoryViewSet, AchievementViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"categories", AchievementCategoryViewSet, basename="category")
router.register(r"achievements", AchievementViewSet, basename="achievement")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = router.urls
