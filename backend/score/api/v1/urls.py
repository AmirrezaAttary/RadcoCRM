from django.urls import path

from . import views


urlpatterns = [
    path(
    "admin/employees/<int:employee_id>/adjust/",
    views.AdminScoreAdjustmentView.as_view(),
    name="admin-employee-score-adjustment",
    ),
    path(
        "employees/<int:employee_id>/",
        views.EmployeeScoreView.as_view(),
        name="employee-score",
    ),
    path(
        "employees/<int:employee_id>/history/",
        views.EmployeeScoreHistoryView.as_view(),
        name="employee-score-history",
    ),
]