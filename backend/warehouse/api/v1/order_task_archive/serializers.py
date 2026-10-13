from rest_framework import serializers

from warehouse.models.order_task_archive import OrderTaskArchive


class OrderTaskArchiveListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrderTaskArchive

        fields = [
            "id",
            "order_task",
            "task_id",
            "status",
            "title",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "items",

            "case",
            "customer",
            "department",
            "current_step",
            "created_by",
            "performed_by",
            "assigned_employees",
            "archived_at",
        ]


class OrderTaskArchiveDetailSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrderTaskArchive

        fields = [
            "id",
            "order_task",
            "task_id",
            "status",
            "title",
            "description",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "items",

            "case",
            "customer",
            "department",
            "current_step",
            "created_by",
            "performed_by",
            "assigned_employees",

            "note",
            "completion_note",
            "file",
            "order_task_created_at",
            "archived_at",
        ]