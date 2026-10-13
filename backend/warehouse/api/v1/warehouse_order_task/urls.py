from django.urls import path

from .views import (
    OrderTaskCreateView,
    OrderTaskListView,
    OrderTaskDetailView,
    OrderTaskUpdateView,

    OrderTaskActivateView,
    OrderTaskDeactivateView,

    OrderTaskDeadlineListView,
    OrderTaskDeadlineDetailView,

    OrderTaskAttachmentListView,
    OrderTaskAttachmentCreateView,
    OrderTaskAttachmentDetailView,
    OrderTaskAttachmentUpdateView,
    OrderTaskAttachmentDeleteView,
)


urlpatterns = [

    path(
        "",
        OrderTaskListView.as_view(),
        name="order-task-list",
    ),

    path(
        "create/",
        OrderTaskCreateView.as_view(),
        name="order-task-create",
    ),

    path(
        "<int:pk>/",
        OrderTaskDetailView.as_view(),
        name="order-task-detail",
    ),

    path(
        "<int:pk>/update/",
        OrderTaskUpdateView.as_view(),
        name="order-task-update",
    ),

    path(
        "<int:pk>/activate/",
        OrderTaskActivateView.as_view(),
        name="order-task-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        OrderTaskDeactivateView.as_view(),
        name="order-task-deactivate",
    ),

    path(
        "deadlines/",
        OrderTaskDeadlineListView.as_view(),
        name="order-task-deadline-list",
    ),

    path(
        "deadlines/<int:pk>/",
        OrderTaskDeadlineDetailView.as_view(),
        name="order-task-deadline-detail",
    ),

    path(
        "attachment/",
        OrderTaskAttachmentListView.as_view(),
        name="order-task-attachment-list",
    ),

    path(
        "attachment/create/",
        OrderTaskAttachmentCreateView.as_view(),
        name="order-task-attachment-create",
    ),

    path(
        "attachment/<int:pk>/",
        OrderTaskAttachmentDetailView.as_view(),
        name="order-task-attachment-detail",
    ),

    path(
        "attachment/<int:pk>/update/",
        OrderTaskAttachmentUpdateView.as_view(),
        name="order-task-attachment-update",
    ),

    path(
        "attachment/<int:pk>/delete/",
        OrderTaskAttachmentDeleteView.as_view(),
        name="order-task-attachment-delete",
    ),
]