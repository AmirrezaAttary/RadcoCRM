from rest_framework import serializers

from quality_control.models.quality_control import QualityControl


class QualityControlSerializer(serializers.ModelSerializer):

    purchase_task_id = serializers.IntegerField(
        source="purchase_task.id",
        read_only=True,
    )

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

    product_id = serializers.IntegerField(
        source="purchase_task.product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="purchase_task.product.name",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )


    checked_by_name = serializers.CharField(
        source="checked_by.user.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = QualityControl

        fields = [
            "id",
            "purchase_task_id",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "product_id",
            "product_name",

            "status",
            "status_display",

            "active",

            "note",
            "file",

            "checked_by",
            "checked_by_name",

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

            "active",

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


class QualityControlActivateSerializer(serializers.Serializer):
    pass


class QualityControlDeactivateSerializer(serializers.Serializer):
    pass