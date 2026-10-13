from django.urls import path

from .views import (
    PurchaseTaskListCreateView,
    PurchaseTaskInitialCreateView,
    PurchaseTaskDetailView,
    PurchaseTaskAdvanceView,
    PurchaseTaskRevertView,
    PurchaseTaskHistoryDetailView,
    PurchaseTaskHistoryListView,
    PurchaseTaskStatusView,
)

urlpatterns = [
    path(
        "",
        PurchaseTaskListCreateView.as_view(),
        name="purchase-task-list-create",
    ),
    path(
        "initial/",
        PurchaseTaskInitialCreateView.as_view(),
        name="purchase-task-initial-create",
    ),
    path(
        "<int:pk>/",
        PurchaseTaskDetailView.as_view(),
        name="purchase-task-detail",
    ),
    path(
        "<int:pk>/advance/",
        PurchaseTaskAdvanceView.as_view(),
        name="purchase-task-advance",
    ),
    path(
        "<int:pk>/revert/",
        PurchaseTaskRevertView.as_view(),
        name="purchase-task-revert",
    ),
    path(
        "history/",
        PurchaseTaskHistoryListView.as_view(),
        name="purchase-task-history-list",
    ),
    path(
        "<int:pk>/history/",
        PurchaseTaskHistoryDetailView.as_view(),
        name="purchase-task-history-detail",
    ),
    path(
        "<int:pk>/status/",
        PurchaseTaskStatusView.as_view(),
        name="purchase-task-status",
    ),
]