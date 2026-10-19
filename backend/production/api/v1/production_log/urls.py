from django.urls import path

from .views import (
    ProductionLogListView,
    ProductionLogCreateView,
    ProductionLogDetailView,
    ProductionLogUpdateView,
    ProductionLogDeleteView,
)


urlpatterns = [
    path(
        "",
        ProductionLogListView.as_view(),
        name="production-log-list",
    ),
    path(
        "create/",
        ProductionLogCreateView.as_view(),
        name="production-log-create",
    ),
    path(
        "<int:pk>/",
        ProductionLogDetailView.as_view(),
        name="production-log-detail",
    ),
    path(
        "<int:pk>/update/",
        ProductionLogUpdateView.as_view(),
        name="production-log-update",
    ),
    path(
        "<int:pk>/delete/",
        ProductionLogDeleteView.as_view(),
        name="production-log-delete",
    ),
]
