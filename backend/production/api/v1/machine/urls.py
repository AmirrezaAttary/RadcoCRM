from django.urls import path

from .views import (
    MachineListView,
    MachineCreateView,
    MachineDetailView,
    MachineUpdateView,
    MachineDeleteView,
)


urlpatterns = [
    path(
        "",
        MachineListView.as_view(),
        name="production-machine-list",
    ),
    path(
        "create/",
        MachineCreateView.as_view(),
        name="production-machine-create",
    ),
    path(
        "<int:pk>/",
        MachineDetailView.as_view(),
        name="production-machine-detail",
    ),
    path(
        "<int:pk>/update/",
        MachineUpdateView.as_view(),
        name="production-machine-update",
    ),
    path(
        "<int:pk>/delete/",
        MachineDeleteView.as_view(),
        name="production-machine-delete",
    ),
]
