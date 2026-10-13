from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.InternalTaskArchiveListView.as_view(),
        name="internal-task-archive-list",
    ),

    path(
        "<int:pk>/",
        views.InternalTaskArchiveRetrieveView.as_view(),
        name="internal-task-archive-detail",
    ),
]
