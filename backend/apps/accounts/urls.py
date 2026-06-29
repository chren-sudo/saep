"""
accounts 路由
"""

from django.urls import include, path

from . import views

# Auth 子路由
auth_urlpatterns = [
    path("login/", views.login, name="auth-login"),
    path("refresh/", views.token_refresh, name="auth-refresh"),
    path("profile/", views.profile, name="auth-profile"),
]

# Students 子路由
students_urlpatterns = [
    path("template/", views.student_template, name="student-template"),
    path("import/", views.student_import, name="student-import"),
]

urlpatterns = [
    # Health check (TASK-001.5)
    path("health/", views.health_check, name="health-check"),
    # Auth (TASK-002)
    path("auth/", include(auth_urlpatterns)),
    # Student Import (TASK-007)
    path("students/", include(students_urlpatterns)),
]
