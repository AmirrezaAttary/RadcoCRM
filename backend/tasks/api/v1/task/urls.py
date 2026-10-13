from django.urls import path

from .views import (
    TaskListApi,
    TaskCreateApi,
    TaskDetailApi,
    TaskAdvanceApi,
    TaskRevertApi,
    TaskStepLogListApi,
    TaskUpdateApi,
    TaskDeleteApi,
    TaskCancelApi,
    TaskMarkAsSoldApi,
    TaskStepDeadlineDetailView,
    TaskStepDeadlineUpdateView,
    TaskStepDeadlinePatchView,
    TaskStepDeadlineDeleteView,
    TaskReopenApi,
    CompleteTaskView,
    TaskDeactivateApi,
    TaskActivateApi,

)

app_name = "task"

urlpatterns = [
    path("", TaskListApi.as_view(), name="task-list"),
    path("create/", TaskCreateApi.as_view(), name="task-create"),
    path("<int:pk>/", TaskDetailApi.as_view(), name="task-detail"),
    path("<int:pk>/update/", TaskUpdateApi.as_view(), name="task-update"),
    path("<int:pk>/delete/", TaskDeleteApi.as_view(), name="task-delete"),
    path("<int:pk>/advance/", TaskAdvanceApi.as_view(), name="task-advance"),
    path("<int:pk>/revert/", TaskRevertApi.as_view(), name="task-revert"),
    path("<int:task_id>/logs/", TaskStepLogListApi.as_view(), name="task-step-logs"),
    path("<int:pk>/cancel/", TaskCancelApi.as_view(), name="task-cancel"),
    path("<int:pk>/mark-as-sold/", TaskMarkAsSoldApi.as_view(), name="task-mark-as-sold"),
    path(
        "<int:pk>/complete/",
        CompleteTaskView.as_view(),
        name="task-complete",
    ),
    path(
        "<int:pk>/reopen/",
        TaskReopenApi.as_view(),
        name="task-reopen",
    ),

    path(
        "<int:task_id>/steps/<int:department_step_id>/deadline/",
        TaskStepDeadlineDetailView.as_view(),
        name="task-step-deadline-detail",
    ),

    path(
        "<int:task_id>/steps/<int:department_step_id>/deadline/update/",
        TaskStepDeadlineUpdateView.as_view(),
        name="task-step-deadline-update",
    ),

    path(
        "<int:task_id>/steps/<int:department_step_id>/deadline/patch/",
        TaskStepDeadlinePatchView.as_view(),
        name="task-step-deadline-patch",
    ),

    path(
        "<int:task_id>/steps/<int:department_step_id>/deadline/delete/",
        TaskStepDeadlineDeleteView.as_view(),
        name="task-step-deadline-delete",
    ),
    
    path(
        "<int:pk>/deactivate/",
        TaskDeactivateApi.as_view(),
        name="task-deactivate",
    ),

    path(
        "<int:pk>/activate/",
        TaskActivateApi.as_view(),
        name="task-activate",
    ),
]