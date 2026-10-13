from rest_framework import serializers

from quality_control.models.quality_control import QualityControl


class QualityControlSerializer(serializers.ModelSerializer):

    # =========================================================
    # Purchase Task
    # =========================================================

    purchase_task_id = serializers.IntegerField(
        source="purchase_task.id",
        read_only=True,
    )

    # =========================================================
    # Warehouse
    # =========================================================

    warehouse_id = serializers.IntegerField(
        source="purchase_task.warehouse.id",
        read_only=True,
    )

    warehouse_name = serializers.CharField(
        source="purchase_task.warehouse.name",
        read_only=True,
    )

    warehouse_code = serializers.CharField(
        source="purchase_task.warehouse.code",
        read_only=True,
    )

    # =========================================================
    # Product
    # =========================================================

    product_id = serializers.IntegerField(
        source="purchase_task.product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="purchase_task.product.name",
        read_only=True,
    )

    # =========================================================
    # Status
    # =========================================================

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    # =========================================================
    # Checked By
    # =========================================================

    checked_by_name = serializers.CharField(
        source="checked_by.user.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = QualityControl

        fields = [
            "id",

            # Purchase
            "purchase_task_id",

            # Warehouse
            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            # Product
            "product_id",
            "product_name",

            # Status
            "status",
            "status_display",

            # QC Data
            "note",
            "file",

            # Checker
            "checked_by",
            "checked_by_name",

            # Dates
            "created_at",
            "checked_at",
        ]

        read_only_fields = [
            "id",
            "purchase_task_id",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "product_id",
            "product_name",

            "status",
            "status_display",

            "checked_by",
            "checked_by_name",

            "created_at",
            "checked_at",
        ]


class QualityControlActionSerializer(serializers.Serializer):

    checked_by = serializers.IntegerField()

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )