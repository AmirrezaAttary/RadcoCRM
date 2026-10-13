from django.urls import path, include

urlpatterns = [
    path("products/", include("warehouse.api.v1.product.urls")),
    path("process/", include("warehouse.api.v1.warehouse_process.urls")),
    path("staff/", include("warehouse.api.v1.warehouse_staff.urls")),
    path("task/", include("warehouse.api.v1.warehouse_task.urls")),
    path("order_task/", include("warehouse.api.v1.warehouse_order_task.urls")),
    path("order_task_archive/", include("warehouse.api.v1.order_task_archive.urls")),
    path("warehouse_task_archive/", include("warehouse.api.v1.warehouse_task_archive.urls")),
    path("warehouse/", include("warehouse.api.v1.warehouse.urls")),
]