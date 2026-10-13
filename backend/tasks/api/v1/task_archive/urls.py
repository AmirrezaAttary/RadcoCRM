from django.urls import path

from .views import (
    TaskArchiveListView,
    TaskArchiveDetailView,
)


urlpatterns = [
    path(
        "",
        TaskArchiveListView.as_view(),
        name="task-archive-list",
    ),
    path(
        "<int:id>/",
        TaskArchiveDetailView.as_view(),
        name="task-archive-detail",
    ),
]