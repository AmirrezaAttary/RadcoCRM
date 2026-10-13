from django.urls import path

from .views import (
    OrderTaskArchiveListView,
    OrderTaskArchiveDetailView,
)


urlpatterns = [
    path(
        "",
        OrderTaskArchiveListView.as_view(),
        name="order-task-archive-list",
    ),

    path(
        "<int:pk>/",
        OrderTaskArchiveDetailView.as_view(),
        name="order-task-archive-detail",
    ),
]