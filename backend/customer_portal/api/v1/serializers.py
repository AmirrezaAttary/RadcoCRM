from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers

from customers.models import Customer
from warehouse.api.v1.product.serializers import (
    AreaUnitSerializer,
    CountUnitSerializer,
    DimensionUnitSerializer,
    VolumeUnitSerializer,
    WeightUnitSerializer,
)
from warehouse.models.product import Product

from ...models import CustomerOrder, CustomerOrderItem, CustomerPortalAccount
from ...services import generate_password, products_with_stock


# ───────────────────────── مدیریت حساب (ادمین) ─────────────────────────

class AccountListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone_number", read_only=True)
    company_name = serializers.CharField(source="customer.company_name", read_only=True)
    granted_by_username = serializers.CharField(source="granted_by.username", read_only=True)

    class Meta:
        model = CustomerPortalAccount
        fields = (
            "id",
            "customer",
            "customer_name",
            "customer_phone",
            "company_name",
            "username",
            "is_active",
            "granted_by",
            "granted_by_username",
            "last_login",
            "created_at",
        )


class AccountCreateSerializer(serializers.ModelSerializer):
    """
    اگر password ارسال نشود، رمز تصادفی ساخته و فقط همین یک بار
    در generated_password برگردانده می‌شود (بعداً قابل مشاهده نیست).
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
    )
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = CustomerPortalAccount
        fields = (
            "id",
            "customer",
            "username",
            "password",
            "generated_password",
            "is_active",
        )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop("password", None)
        generated = not raw_password

        if generated:
            raw_password = generate_password()

        account = CustomerPortalAccount(
            granted_by=self.context["request"].user,
            **validated_data,
        )
        account.set_password(raw_password)
        account.save()

        if generated:
            account.generated_password = raw_password

        return account


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPortalAccount
        fields = ("username", "is_active")


class AccountPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False,
        write_only=True,
        trim_whitespace=False,
    )

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


# ───────────────────────────── ورود مشتری ─────────────────────────────

class PortalLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class PortalMeSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer.id", read_only=True)
    full_name = serializers.CharField(source="customer.full_name", read_only=True)
    company_name = serializers.CharField(source="customer.company_name", read_only=True)
    phone_number = serializers.CharField(source="customer.phone_number", read_only=True)

    class Meta:
        model = CustomerPortalAccount
        fields = (
            "id",
            "username",
            "customer_id",
            "full_name",
            "company_name",
            "phone_number",
        )


# ───────────────────────────── کالاها ─────────────────────────────

class PortalProductSerializer(serializers.ModelSerializer):
    """نسخهٔ عمومی کالا: بدون کد قفسه و اطلاعات داخلی انبار."""

    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    available_quantity = serializers.FloatField(read_only=True)

    dimension_unit_detail = DimensionUnitSerializer(source="dimension_unit", read_only=True)
    weight_unit_detail = WeightUnitSerializer(source="weight_unit", read_only=True)
    volume_unit_detail = VolumeUnitSerializer(source="volume_unit", read_only=True)
    area_unit_detail = AreaUnitSerializer(source="area_unit", read_only=True)
    count_unit_detail = CountUnitSerializer(source="count_unit", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sale_price",
            "category",
            "category_name",
            "unit_type",
            "available_quantity",
            "dimension_unit_detail",
            "weight_unit_detail",
            "volume_unit_detail",
            "area_unit_detail",
            "count_unit_detail",
        )


# ───────────────────────────── سفارش ─────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CustomerOrderItem
        fields = ("id", "product", "product_name", "quantity", "unit_price", "line_total")

    def get_line_total(self, obj) -> int:
        return int(round(float(obj.unit_price) * obj.quantity))


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone_number", read_only=True)
    company_name = serializers.CharField(source="customer.company_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CustomerOrder
        fields = (
            "id",
            "customer",
            "customer_name",
            "customer_phone",
            "company_name",
            "status",
            "status_display",
            "note",
            "staff_note",
            "items",
            "total_price",
            "created_at",
            "updated_at",
        )

    def get_total_price(self, obj) -> int:
        return sum(
            int(round(float(i.unit_price) * i.quantity)) for i in obj.items.all()
        )


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.FloatField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("تعداد باید بیشتر از صفر باشد.")
        return value


class OrderCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")
    items = OrderItemInputSerializer(many=True, allow_empty=False)

    def validate_items(self, items):
        ids = [i["product"].pk for i in items]

        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("یک کالا نباید بیش از یک بار در سفارش بیاید.")

        stock = dict(
            products_with_stock()
            .filter(pk__in=ids)
            .values_list("pk", "available_quantity")
        )

        errors = []
        for item in items:
            product = item["product"]
            available = stock.get(product.pk, 0)
            if item["quantity"] > available:
                errors.append(
                    f"موجودی «{product.name}» کافی نیست (موجودی فعلی: {available:g})."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return items

    @transaction.atomic
    def create(self, validated_data):
        account = self.context["request"].user

        order = CustomerOrder.objects.create(
            customer=account.customer,
            account=account,
            note=validated_data.get("note", ""),
        )

        CustomerOrderItem.objects.bulk_create([
            CustomerOrderItem(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["product"].sale_price,
            )
            for item in validated_data["items"]
        ])

        return order


class OrderStatusSerializer(serializers.Serializer):
    """تصمیم کارمند: تأیید یا رد سفارش."""

    status = serializers.ChoiceField(
        choices=[
            CustomerOrder.Status.CONFIRMED,
            CustomerOrder.Status.REJECTED,
        ]
    )
    staff_note = serializers.CharField(required=False, allow_blank=True, default="")
