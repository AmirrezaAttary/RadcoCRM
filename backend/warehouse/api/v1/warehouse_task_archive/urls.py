from django.urls import path

from .views import (
    WarehouseTaskArchiveListView,
    WarehouseTaskArchiveDetailView,
)


urlpatterns = [

    path(
        "",
        WarehouseTaskArchiveListView.as_view(),
        name="warehouse-task-archive-list",
    ),

    path(
        "<int:pk>/",
        WarehouseTaskArchiveDetailView.as_view(),
        name="warehouse-task-archive-detail",
    ),

]