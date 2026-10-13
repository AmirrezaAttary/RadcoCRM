from django.urls import include, path

app_name = "tasks"

urlpatterns = [
    path("cases/", include("tasks.api.v1.case.urls")),
    path("tasks/", include("tasks.api.v1.task.urls")),
    path("tasks/", include("tasks.api.v1.task_attachment.urls")),
    path("internal_task/", include("tasks.api.v1.internal_task.urls")),
    path("task_archive/", include("tasks.api.v1.task_archive.urls")),
    path("internal_task_archive/", include("tasks.api.v1.internal_task_archive.urls")),
    path("internal_task_routine/", include("tasks.api.v1.internal_task_routine.urls")),
]