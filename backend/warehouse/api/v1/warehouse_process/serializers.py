from rest_framework import serializers

from warehouse.models.warehouse_process import (
    InventoryStock,
    StockTransaction,
)

from warehouse.models.warehouse_stock_out import (
    WarehouseStockOut,
    WarehouseStockOutItem,
)


class InventoryStockSerializer(
    serializers.ModelSerializer
):

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

    unit_label = serializers.SerializerMethodField()

    performed_by = serializers.SerializerMethodField()

    class Meta:
        model = InventoryStock

        fields = [
            "id",

            "warehouse",
            "warehouse_name",
            "warehouse_code",

            "product",
            "product_name",

            "initial_quantity",
            "current_quantity",
            "minimum_stock",
            "maximum_stock",

            "unit_label",
            "performed_by",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "current_quantity",
            "created_at",
            "updated_at",
        ]

    def get_unit_label(self, obj):

        labels = {
            "dimension": "ابعاد",
            "weight": "وزن",
            "volume": "حجم",
            "area": "مساحت",
            "count": "عدد",
        }

        return labels.get(
            obj.product.unit_type,
            "",
        )

    def get_performed_by(self, obj):

        transactions = getattr(
            obj.product,
            "initial_transactions",
            [],
        )

        transaction = next(
            (
                transaction
                for transaction in transactions
                if (
                    transaction.warehouse_id
                    == obj.warehouse_id
                    and
                    transaction.product_id
                    == obj.product_id
                )
            ),
            None,
        )

        if not transaction:
            return None

        if not transaction.performed_by:
            return None

        if not transaction.performed_by.employee:
            return None

        return {
            "id": transaction.performed_by.id,
            "full_name": (
                transaction
                .performed_by
                .employee
                .user
                .profile
                .full_name
            ),
        }


class InitialStockSerializer(
    serializers.Serializer
):

    warehouse_id = serializers.IntegerField()

    product_id = serializers.IntegerField()

    performed_by_id = serializers.IntegerField(
        required=True
    )

    quantity = serializers.FloatField(
        min_value=0.0001
    )

    minimum_stock = serializers.FloatField(
        min_value=0
    )

    maximum_stock = serializers.FloatField(
        min_value=0
    )

    def validate(self, attrs):

        quantity = attrs["quantity"]
        minimum_stock = attrs["minimum_stock"]
        maximum_stock = attrs["maximum_stock"]

        if maximum_stock < minimum_stock:
            raise serializers.ValidationError({
                "maximum_stock": (
                    "حداکثر موجودی نمی‌تواند کمتر "
                    "از حداقل موجودی باشد."
                )
            })

        if quantity < minimum_stock:
            raise serializers.ValidationError({
                "quantity": (
                    f"موجودی اولیه نمی‌تواند کمتر "
                    f"از حداقل موجودی "
                    f"({minimum_stock}) باشد."
                )
            })

        if quantity > maximum_stock:
            raise serializers.ValidationError({
                "quantity": (
                    f"موجودی اولیه نمی‌تواند بیشتر "
                    f"از حداکثر موجودی "
                    f"({maximum_stock}) باشد."
                )
            })

        return attrs


class StockInSerializer(
    serializers.Serializer
):

    warehouse_id = serializers.IntegerField()

    product_id = serializers.IntegerField()

    performed_by_id = serializers.IntegerField()

    quantity = serializers.FloatField(
        min_value=0.0001
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class StockOutItemRequestSerializer(
    serializers.Serializer
):

    product_id = serializers.IntegerField()

    quantity = serializers.FloatField(
        min_value=0.0001
    )

    reason = serializers.ChoiceField(
        choices=StockTransaction.StockOutReason.choices,
        default=StockTransaction.StockOutReason.SALE,
    )


class StockOutSerializer(
    serializers.Serializer
):

    warehouse_id = serializers.IntegerField()

    performed_by_id = serializers.IntegerField(
        required=True
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    items = StockOutItemRequestSerializer(
        many=True,
        allow_empty=False,
    )

    def to_internal_value(self, data):
        """
        Supports:

        1. application/json
        2. multipart/form-data

        In multipart/form-data, `items` is received
        as a JSON string.
        """

        if hasattr(data, "get"):
            items = data.get("items")
        else:
            items = None

        if isinstance(items, str):

            import json

            try:
                items = json.loads(items)

            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    "items": (
                        "فرمت items صحیح نیست. "
                        "باید یک JSON معتبر باشد."
                    )
                })

            data = data.copy()

            if hasattr(data, "dict"):
                data = data.dict()

            data["items"] = items

        return super().to_internal_value(data)

    def validate_items(self, value):

        product_ids = [
            item["product_id"]
            for item in value
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "یک کالا نمی‌تواند بیشتر از یک بار "
                "در یک فاکتور خروج ثبت شود."
            )

        return value


class StockTransactionSerializer(
    serializers.ModelSerializer
):

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

    minimum_stock = serializers.SerializerMethodField()

    maximum_stock = serializers.SerializerMethodField()

    performed_by_name = serializers.SerializerMethodField()

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True,
    )

    stock_out_reason_display = serializers.CharField(
        source="get_stock_out_reason_display",
        read_only=True,
    )

    class Meta:
        model = StockTransaction

        fields = [
            "id",

            "warehouse",
            "warehouse_name",
            "warehouse_code",

            "product",
            "product_name",

            "performed_by",
            "performed_by_name",

            "transaction_type",
            "transaction_type_display",

            "quantity_changed",
            "quantity_before",
            "quantity_after",

            "minimum_stock",
            "maximum_stock",

            "stock_out_reason",
            "stock_out_reason_display",

            "note",

            "transaction_date",
            "created_at",
        ]

        read_only_fields = fields

    def get_minimum_stock(self, obj):

        stock = (
            InventoryStock.objects
            .filter(
                warehouse_id=obj.warehouse_id,
                product_id=obj.product_id,
            )
            .first()
        )

        return (
            stock.minimum_stock
            if stock
            else None
        )

    def get_maximum_stock(self, obj):

        stock = (
            InventoryStock.objects
            .filter(
                warehouse_id=obj.warehouse_id,
                product_id=obj.product_id,
            )
            .first()
        )

        return (
            stock.maximum_stock
            if stock
            else None
        )

    def get_performed_by_name(self, obj):

        if not obj.performed_by:
            return None

        if not obj.performed_by.employee:
            return None

        return (
            obj.performed_by
            .employee
            .user
            .profile
            .full_name
        )


class WarehouseStockOutItemSerializer(
    serializers.ModelSerializer
):

    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    reason_display = serializers.CharField(
        source="get_reason_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    stock_transaction_id = serializers.IntegerField(
        source="stock_transaction.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = WarehouseStockOutItem

        fields = [
            "id",

            "product_id",
            "product_name",

            "quantity",

            "reason",
            "reason_display",

            "status",
            "status_display",

            "quantity_before",
            "quantity_after",

            "stock_transaction_id",

            "error_message",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class WarehouseStockOutSerializer(
    serializers.ModelSerializer
):

    warehouse_id = serializers.IntegerField(
        source="warehouse.id",
        read_only=True,
    )

    warehouse_name = serializers.CharField(
        source="warehouse.name",
        read_only=True,
    )

    warehouse_code = serializers.CharField(
        source="warehouse.code",
        read_only=True,
    )

    performed_by_id = serializers.IntegerField(
        source="performed_by.id",
        read_only=True,
    )

    performed_by_name = serializers.SerializerMethodField()

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    items = WarehouseStockOutItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = WarehouseStockOut

        fields = [
            "id",

            "warehouse_id",
            "warehouse_name",
            "warehouse_code",

            "performed_by_id",
            "performed_by_name",

            "status",
            "status_display",

            "note",
            "file",

            "created_at",
            "updated_at",

            "items",
        ]

        read_only_fields = fields

    def get_performed_by_name(self, obj):

        if not obj.performed_by:
            return None

        if not obj.performed_by.employee:
            return None

        return (
            obj.performed_by
            .employee
            .user
            .profile
            .full_name
        )
    

class InventoryStockLimitSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InventoryStock
        fields = [
            "minimum_stock",
            "maximum_stock",
        ]

    def validate(self, attrs):

        instance = self.instance

        minimum_stock = attrs.get(
            "minimum_stock",
            instance.minimum_stock
        )

        maximum_stock = attrs.get(
            "maximum_stock",
            instance.maximum_stock
        )

        if minimum_stock < 0:
            raise serializers.ValidationError({
                "minimum_stock": (
                    "حداقل موجودی نمی‌تواند کمتر از صفر باشد."
                )
            })

        if maximum_stock < 0:
            raise serializers.ValidationError({
                "maximum_stock": (
                    "حداکثر موجودی نمی‌تواند کمتر از صفر باشد."
                )
            })

        if maximum_stock < minimum_stock:
            raise serializers.ValidationError({
                "maximum_stock": (
                    "حداکثر موجودی نمی‌تواند کمتر "
                    "از حداقل موجودی باشد."
                )
            })

        return attrs
