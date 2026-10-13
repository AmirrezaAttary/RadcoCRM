from rest_framework import serializers

from purchasing.models.purchase_task import PurchaseTask
from warehouse.models.warehouse_task import WarehouseTask
from warehouse.models.warehouse_task_archive import (
    WarehouseTaskArchive,
)


class WarehouseTaskArchiveSerializer(
    serializers.ModelSerializer
):

    status_display = serializers.SerializerMethodField()

    source_display = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseTaskArchive

        fields = [
            "id",
            "warehouse_task",

            "purchase_task_id",
            "purchase_task_title",
            "purchase_task_source",
            "source_display",
            "purchase_task_created_by_id",
            "purchase_task_created_by_employee_id",
            "purchase_task_created_by_full_name",

            "quality_control_id",
            "quality_control_title",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "product_id",
            "product_name",

            "minimum_stock",
            "maximum_stock",
            "quantity_before",
            "quantity_after",

            "expected_quantity",
            "received_quantity",

            "status",
            "status_display",

            "assigned_to_id",
            "assigned_to_employee_id",
            "assigned_to_full_name",

            "note",
            "file",

            "task_created_at",
            "task_updated_at",
            "completed_at",
            "archived_at",
        ]

        read_only_fields = [
            "id",
            "warehouse_task",

            "purchase_task_id",
            "purchase_task_title",
            "purchase_task_source",
            "source_display",
            "purchase_task_created_by_id",
            "purchase_task_created_by_employee_id",
            "purchase_task_created_by_full_name",

            "quality_control_id",
            "quality_control_title",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "product_id",
            "product_name",

            "minimum_stock",
            "maximum_stock",

            "quantity_before",
            "quantity_after",

            "expected_quantity",
            "received_quantity",

            "status",
            "status_display",

            "assigned_to_id",
            "assigned_to_employee_id",
            "assigned_to_full_name",

            "note",
            "file",

            "task_created_at",
            "task_updated_at",
            "completed_at",
            "archived_at",
        ]

    def get_status_display(self, obj):
        return dict(
            WarehouseTask.Status.choices
        ).get(
            obj.status,
            obj.status,
        )

    def get_source_display(self, obj):
        return dict(
            PurchaseTask.Source.choices
        ).get(
            obj.purchase_task_source,
            obj.purchase_task_source,
        )