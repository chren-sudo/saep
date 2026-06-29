"""
organizations 路由
"""

from django.urls import path

from .views import ClassStudentViewSet, EvaluatorViewSet

evaluator_list = EvaluatorViewSet.as_view({"get": "list", "post": "create"})
evaluator_detail = EvaluatorViewSet.as_view({"delete": "destroy"})
student_list = ClassStudentViewSet.as_view({"get": "list"})

urlpatterns = [
    path(
        "classes/<int:class_id>/evaluators/",
        evaluator_list,
        name="class-evaluators-list",
    ),
    path(
        "classes/<int:class_id>/evaluators/<int:pk>/",
        evaluator_detail,
        name="class-evaluators-detail",
    ),
    path(
        "classes/<int:class_id>/students/",
        student_list,
        name="class-students-list",
    ),
]
