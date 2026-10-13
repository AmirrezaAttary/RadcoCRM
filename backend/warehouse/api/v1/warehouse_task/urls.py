from django.urls import path

from .views import (
    WarehouseTaskListView,
    WarehouseTaskDetailView,
    WarehouseTaskCompleteView,
    WarehouseTaskInitialCompleteView,
    WarehouseTaskCancelView,
    WarehouseTaskReopenView,
    WarehouseTaskActivateView,
    WarehouseTaskDeactivateView,
)


urlpatterns = [
    path(
        "",
        WarehouseTaskListView.as_view(),
        name="warehouse-task-list",
    ),

    path(
        "<int:pk>/",
        WarehouseTaskDetailView.as_view(),
        name="warehouse-task-detail",
    ),

    path(
        "<int:pk>/complete/",
        WarehouseTaskCompleteView.as_view(),
        name="warehouse-task-complete",
    ),

    path(
        "<int:pk>/complete-initial/",
        WarehouseTaskInitialCompleteView.as_view(),
        name="warehouse-task-complete-initial",
    ),

    path(
        "<int:pk>/cancel/",
        WarehouseTaskCancelView.as_view(),
        name="warehouse-task-cancel",
    ),

    path(
        "<int:pk>/reopen/",
        WarehouseTaskReopenView.as_view(),
        name="warehouse-task-reopen",
    ),

    path(
        "<int:pk>/activate/",
        WarehouseTaskActivateView.as_view(),
        name="warehouse-task-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        WarehouseTaskDeactivateView.as_view(),
        name="warehouse-task-deactivate",
    ),
]