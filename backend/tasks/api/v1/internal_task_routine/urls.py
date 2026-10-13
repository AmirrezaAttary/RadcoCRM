from django.urls import path

from tasks.api.v1.internal_task_routine.views import (
    InternalTaskRoutineListView,
    InternalTaskRoutineCreateView,
    InternalTaskRoutineRetrieveView,
    InternalTaskRoutinePatchView,
    InternalTaskRoutineDestroyView,
)


urlpatterns = [

    path(
        "",
        InternalTaskRoutineListView.as_view(),
        name="internal-task-routine-list",
    ),

    path(
        "create/",
        InternalTaskRoutineCreateView.as_view(),
        name="internal-task-routine-create",
    ),

    path(
        "<int:pk>/",
        InternalTaskRoutineRetrieveView.as_view(),
        name="internal-task-routine-retrieve",
    ),

    path(
        "<int:pk>/patch/",
        InternalTaskRoutinePatchView.as_view(),
        name="internal-task-routine-patch",
    ),

    path(
        "<int:pk>/delete/",
        InternalTaskRoutineDestroyView.as_view(),
        name="internal-task-routine-delete",
    ),
]