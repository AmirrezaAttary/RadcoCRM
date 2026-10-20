from rest_framework import serializers

from purchasing.models.purchase_task import PurchaseTask
from warehouse.models.warehouse_task import WarehouseTask


class WarehouseTaskSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    warehouse_name = serializers.CharField(
        source="warehouse.name",
        read_only=True,
        allow_null=True,
    )

    warehouse_code = serializers.CharField(
        source="warehouse.code",
        read_only=True,
        allow_null=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    shelf_code = serializers.CharField(
        source="product.shelf_code",
        read_only=True,
    )

    assigned_to_name = serializers.CharField(
        source="assigned_to.employee.full_name",
        read_only=True,
        allow_null=True,
    )

    purchase_task_id = serializers.IntegerField(
        source="purchase_task.id",
        read_only=True,
        allow_null=True,
    )

    purchase_task_source = serializers.SerializerMethodField()

    purchase_task_source_display = serializers.SerializerMethodField()

    quality_control_id = serializers.IntegerField(
        source="quality_control.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = WarehouseTask

        fields = [
            "id",
            "purchase_task_id",
            "purchase_task_source",
            "purchase_task_source_display",
            "quality_control_id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "product",
            "product_name",
            "shelf_code",
            "expected_quantity",
            "received_quantity",
            "assigned_to",
            "assigned_to_name",
            "status",
            "status_display",
            "note",
            "file",
            "created_at",
            "completed_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "purchase_task_id",
            "purchase_task_source",
            "purchase_task_source_display",
            "quality_control_id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "product",
            "product_name",
            "shelf_code",
            "expected_quantity",
            "received_quantity",
            "assigned_to",
            "assigned_to_name",
            "status",
            "status_display",
            "created_at",
            "completed_at",
            "updated_at",
        ]

    def get_purchase_task_source(self, obj):
        if not obj.purchase_task:
            return None

        return obj.purchase_task.source

    def get_purchase_task_source_display(self, obj):
        if not obj.purchase_task:
            return None

        return dict(
            PurchaseTask.Source.choices
        ).get(
            obj.purchase_task.source,
            obj.purchase_task.source,
        )


class WarehouseTaskCompleteSerializer(serializers.Serializer):

    assigned_to = serializers.IntegerField(
        min_value=1,
    )

    received_quantity = serializers.FloatField(
        min_value=0.0001,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )


class WarehouseTaskInitialCompleteSerializer(serializers.Serializer):

    warehouse = serializers.IntegerField(
        min_value=1,
    )

    quantity = serializers.FloatField(
        min_value=0.0001,
    )

    performed_by_id = serializers.IntegerField(
        min_value=1,
    )

    minimum_stock = serializers.FloatField(
        min_value=0,
    )

    maximum_stock = serializers.FloatField(
        min_value=0.0001,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        if attrs["minimum_stock"] > attrs["maximum_stock"]:
            raise serializers.ValidationError(
                "حداقل موجودی نمی‌تواند بیشتر از حداکثر موجودی باشد."
            )

        return attrs


class WarehouseTaskCancelSerializer(serializers.Serializer):

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


class WarehouseTaskReopenSerializer(serializers.Serializer):
    pass
