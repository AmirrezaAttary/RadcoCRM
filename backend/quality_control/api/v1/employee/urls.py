from django.urls import path

from .views import (
    QualityControlEmployeeListView,
    QualityControlEmployeeCreateView,
    QualityControlEmployeeDetailView,
    QualityControlEmployeeUpdateView,
    QualityControlEmployeeDeleteView,
)


urlpatterns = [
    path(
        "",
        QualityControlEmployeeListView.as_view(),
        name="quality-control-employee-list",
    ),
    path(
        "create/",
        QualityControlEmployeeCreateView.as_view(),
        name="quality-control-employee-create",
    ),
    path(
        "<int:pk>/",
        QualityControlEmployeeDetailView.as_view(),
        name="quality-control-employee-detail",
    ),
    path(
        "<int:pk>/update/",
        QualityControlEmployeeUpdateView.as_view(),
        name="quality-control-employee-update",
    ),
    path(
        "<int:pk>/delete/",
        QualityControlEmployeeDeleteView.as_view(),
        name="quality-control-employee-delete",
    ),
]
