from rest_framework import serializers

from purchasing.models.purchase_task import PurchaseTask
from purchasing.models.purchase_employee import PurchaseProcessEmployee
from purchasing.api.v1.purchase_attachments.serializers import (
    PurchaseTaskAttachmentListSerializer,
)


class PurchaseTaskSerializer(serializers.ModelSerializer):

    warehouse_name = serializers.CharField(
        source="warehouse.name",
        read_only=True,
    )

    warehouse_code = serializers.CharField(
        source="warehouse.code",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    process_step_title = serializers.CharField(
        source="process_step.title",
        read_only=True,
    )

    process_step_order = serializers.IntegerField(
        source="process_step.order",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    source_display = serializers.CharField(
        source="get_source_display",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.employee.user.profile.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PurchaseTask

        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "product",
            "product_name",
            "process_step",
            "process_step_title",
            "process_step_order",
            "minimum_stock",
            "maximum_stock",
            "quantity_after",
            "purchase_quantity",
            "source",
            "source_display",
            "created_by",
            "created_by_name",
            "status",
            "status_display",
            "active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "warehouse_name",
            "warehouse_code",
            "product_name",
            "process_step_title",
            "process_step_order",
            "minimum_stock",
            "maximum_stock",
            "quantity_after",
            "source",
            "source_display",
            "created_by",
            "created_by_name",
            "status",
            "status_display",
            "active",
            "created_at",
            "updated_at",
        ]


class PurchaseTaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseTask

        fields = [
            "warehouse",
            "product",
            "process_step",
            "purchase_quantity",
        ]

        extra_kwargs = {
            "purchase_quantity": {
                "required": True,
                "allow_null": False,
            },
        }

    def validate_purchase_quantity(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "مقدار مورد نیاز خرید باید بیشتر از صفر باشد."
            )

        return value


class PurchaseTaskInitialCreateSerializer(serializers.Serializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseTask._meta.get_field(
            "product"
        ).remote_field.model.objects.all()
    )

    quantity = serializers.FloatField(
        required=True,
        allow_null=False,
    )

    def validate_quantity(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "مقدار موجودی اولیه باید بیشتر از صفر باشد."
            )

        return value


class PurchaseTaskActionSerializer(serializers.Serializer):

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseProcessEmployee.objects.all()
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


class PurchaseTaskActionResponseSerializer(
    serializers.ModelSerializer
):

    process_step = serializers.CharField(
        source="process_step.title",
        read_only=True,
    )

    class Meta:
        model = PurchaseTask

        fields = [
            "id",
            "product",
            "process_step",
            "status",
            "updated_at",
        ]


class PurchaseTaskHistorySerializer(serializers.ModelSerializer):

    warehouse_name = serializers.CharField(
        source="warehouse.name",
        read_only=True,
    )

    warehouse_code = serializers.CharField(
        source="warehouse.code",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    process_step_title = serializers.CharField(
        source="process_step.title",
        read_only=True,
    )

    process_step_order = serializers.IntegerField(
        source="process_step.order",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    source_display = serializers.CharField(
        source="get_source_display",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.employee.user.profile.full_name",
        read_only=True,
        allow_null=True,
    )

    attachments = PurchaseTaskAttachmentListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = PurchaseTask

        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "product",
            "product_name",
            "process_step",
            "process_step_title",
            "process_step_order",
            "minimum_stock",
            "maximum_stock",
            "quantity_after",
            "purchase_quantity",
            "source",
            "source_display",
            "created_by",
            "created_by_name",
            "status",
            "status_display",
            "active",
            "created_at",
            "updated_at",
            "attachments",
        ]


class PurchaseTaskStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=[
            (
                PurchaseTask.Status.COMPLETED,
                PurchaseTask.Status.COMPLETED.label,
            ),
            (
                PurchaseTask.Status.CANCELLED,
                PurchaseTask.Status.CANCELLED.label,
            ),
        ]
    )


class PurchaseTaskActivateSerializer(serializers.Serializer):
    pass


class PurchaseTaskDeactivateSerializer(serializers.Serializer):
    pass