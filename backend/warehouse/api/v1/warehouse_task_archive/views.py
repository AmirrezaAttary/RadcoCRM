from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.permissions import WarehousePermission
from warehouse.services.warehouse_scope import scope_by_warehouse

from warehouse.models.warehouse_task_archive import (
    WarehouseTaskArchive,
)

from .serializers import (
    WarehouseTaskArchiveSerializer,
)


class WarehouseTaskArchiveListView(
    generics.ListAPIView
):

    search_fields = (
        "purchase_task_title",
        "purchase_task_source",
        "warehouse_name",
        "warehouse_code",
        "product_name",
        "assigned_to_full_name",
        "note",
    )

    queryset = (
        WarehouseTaskArchive.objects
        .select_related(
            "warehouse_task",
            "warehouse_task__warehouse",
            "warehouse_task__purchase_task",
            "warehouse_task__purchase_task__created_by",
            "warehouse_task__purchase_task__created_by__employee_profile",
            "warehouse_task__product",
            "warehouse_task__quality_control",
            "warehouse_task__assigned_to",
            "warehouse_task__assigned_to__employee",
        )
        .order_by("-archived_at")
    )

    serializer_class = WarehouseTaskArchiveSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def get_queryset(self):
        # warehouse_id روی آرشیو snapshot است (نه FK)
        return scope_by_warehouse(
            super().get_queryset(),
            self.request,
            field="warehouse_id",
        )


class WarehouseTaskArchiveDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        WarehouseTaskArchive.objects
        .select_related(
            "warehouse_task",
            "warehouse_task__warehouse",
            "warehouse_task__purchase_task",
            "warehouse_task__purchase_task__created_by",
            "warehouse_task__purchase_task__created_by__employee_profile",
            "warehouse_task__product",
            "warehouse_task__quality_control",
            "warehouse_task__assigned_to",
            "warehouse_task__assigned_to__employee",
        )
    )

    serializer_class = WarehouseTaskArchiveSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )