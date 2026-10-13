from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.InternalTaskListView.as_view(),
        name="internal-task-list",
    ),

    path(
        "create/",
        views.InternalTaskCreateView.as_view(),
        name="internal-task-create",
    ),

    path(
        "<int:pk>/",
        views.InternalTaskRetrieveView.as_view(),
        name="internal-task-detail",
    ),

    path(
        "<int:pk>/update/",
        views.InternalTaskUpdateView.as_view(),
        name="internal-task-update",
    ),

    path(
        "<int:pk>/delete/",
        views.InternalTaskDestroyView.as_view(),
        name="internal-task-delete",
    ),

    path(
        "<int:pk>/activate/",
        views.InternalTaskActivateView.as_view(),
        name="internal-task-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        views.InternalTaskDeactivateView.as_view(),
        name="internal-task-deactivate",
    ),

    path(
        "<int:pk>/complete/",
        views.InternalTaskCompleteView.as_view(),
        name="internal-task-complete",
    ),

    path(
        "<int:pk>/cancel/",
        views.InternalTaskCancelView.as_view(),
        name="internal-task-cancel",
    ),

    path(
        "<int:pk>/reopen/",
        views.InternalTaskReopenView.as_view(),
        name="internal-task-reopen",
    ),

    path(
        "<int:pk>/attachments/",
        views.InternalTaskAttachmentCreateView.as_view(),
        name="internal-task-attachment-create",
    ),

    path(
        "<int:pk>/attachments/<int:attachment_pk>/",
        views.InternalTaskAttachmentDestroyView.as_view(),
        name="internal-task-attachment-delete",
    ),

    path(
        "<int:pk>/deadline/",
        views.InternalTaskDeadlineDetailView.as_view(),
        name="internal-task-deadline-detail",
    ),

    path(
        "<int:pk>/deadline/patch/",
        views.InternalTaskDeadlinePatchView.as_view(),
        name="internal-task-deadline-patch",
    ),

    path(
        "<int:pk>/deadline/update/",
        views.InternalTaskDeadlineUpdateView.as_view(),
        name="internal-task-deadline-update",
    ),

    path(
        "<int:pk>/deadline/delete/",
        views.InternalTaskDeadlineDeleteView.as_view(),
        name="internal-task-deadline-delete",
    ),
]