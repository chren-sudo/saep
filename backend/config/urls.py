"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.achievements.urls")),
    path("api/v1/", include("apps.evaluations.urls")),
    path("api/v1/", include("apps.organizations.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.publicity.urls")),
    path("api/v1/", include("apps.statistics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
