from django.urls import path
from warehouse.api.v1.warehouse_staff.views import (
    WarehouseStaffListView, WarehouseStaffCreateView,
    WarehouseStaffRetrieveView, WarehouseStaffUpdateView, WarehouseStaffDeleteView,
)

urlpatterns = [
    path("", WarehouseStaffListView.as_view(), name="staff-list"),
    path("create/", WarehouseStaffCreateView.as_view(), name="staff-create"),
    path("<int:pk>/", WarehouseStaffRetrieveView.as_view(), name="staff-detail"),
    path("<int:pk>/update/", WarehouseStaffUpdateView.as_view(), name="staff-update"),
    path("<int:pk>/delete/", WarehouseStaffDeleteView.as_view(), name="staff-delete"),
]
