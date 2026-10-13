from django.urls import path

from .views import (
    WarehouseListView,
    WarehouseCreateView,
    WarehouseRetrieveView,
    WarehouseUpdateView,
    WarehousePatchView,
    WarehouseDeleteView,
)


urlpatterns = [

    # GET
    path(
        "",
        WarehouseListView.as_view(),
        name="warehouse-list",
    ),

    # POST
    path(
        "create/",
        WarehouseCreateView.as_view(),
        name="warehouse-create",
    ),

    # GET single
    path(
        "<int:pk>/",
        WarehouseRetrieveView.as_view(),
        name="warehouse-detail",
    ),

    # PUT
    path(
        "<int:pk>/update/",
        WarehouseUpdateView.as_view(),
        name="warehouse-update",
    ),

    # PATCH
    path(
        "<int:pk>/patch/",
        WarehousePatchView.as_view(),
        name="warehouse-patch",
    ),

    # DELETE
    path(
        "<int:pk>/delete/",
        WarehouseDeleteView.as_view(),
        name="warehouse-delete",
    ),
]