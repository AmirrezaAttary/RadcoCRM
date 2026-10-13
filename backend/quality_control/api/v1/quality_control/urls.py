from django.urls import path

from .views import (
    QualityControlListView,
    QualityControlDetailView,
    QualityControlApproveView,
    QualityControlRejectView,
    QualityControlActivateView,
    QualityControlDeactivateView,
)


urlpatterns = [
    path(
        "",
        QualityControlListView.as_view(),
        name="quality-control-list-create",
    ),
    path(
        "<int:pk>/",
        QualityControlDetailView.as_view(),
        name="quality-control-detail",
    ),
    path(
        "<int:pk>/approve/",
        QualityControlApproveView.as_view(),
        name="quality-control-approve",
    ),
    path(
        "<int:pk>/reject/",
        QualityControlRejectView.as_view(),
        name="quality-control-reject",
    ),
    path(
        "<int:pk>/activate/",
        QualityControlActivateView.as_view(),
        name="quality-control-activate",
    ),
    path(
        "<int:pk>/deactivate/",
        QualityControlDeactivateView.as_view(),
        name="quality-control-deactivate",
    ),
]