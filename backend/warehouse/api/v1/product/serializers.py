from rest_framework import serializers
from warehouse.models.product import Product, ProductCategory
from warehouse.models.unit_measurement import (
    DimensionUnit, WeightUnit, VolumeUnit, AreaUnit, CountUnit
)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class DimensionUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimensionUnit
        fields = ["id", "meter", "centimeter", "inch"]


class WeightUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightUnit
        fields = ["id", "gram", "kilogram", "milligram", "ton"]


class VolumeUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolumeUnit
        fields = ["id", "liter", "milliliter", "gallon"]


class AreaUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaUnit
        fields = ["id", "square_meter", "square_centimeter"]


class CountUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountUnit
        fields = ["id", "quantity_per_unit"]


UNIT_MAP = {
    "dimension": ("dimension_unit_data", "dimension_unit", DimensionUnit, DimensionUnitSerializer),
    "weight":    ("weight_unit_data",    "weight_unit",    WeightUnit,    WeightUnitSerializer),
    "volume":    ("volume_unit_data",    "volume_unit",    VolumeUnit,    VolumeUnitSerializer),
    "area":      ("area_unit_data",      "area_unit",      AreaUnit,      AreaUnitSerializer),
    "count":     ("count_unit_data",     "count_unit",     CountUnit,     CountUnitSerializer),
}


class ProductSerializer(serializers.ModelSerializer):
    category_detail = ProductCategorySerializer(source="category", read_only=True)

    dimension_unit_detail = DimensionUnitSerializer(source="dimension_unit", read_only=True)
    weight_unit_detail    = WeightUnitSerializer(source="weight_unit",    read_only=True)
    volume_unit_detail    = VolumeUnitSerializer(source="volume_unit",    read_only=True)
    area_unit_detail      = AreaUnitSerializer(source="area_unit",        read_only=True)
    count_unit_detail     = CountUnitSerializer(source="count_unit",      read_only=True)

    dimension_unit_data = DimensionUnitSerializer(write_only=True, required=False)
    weight_unit_data    = WeightUnitSerializer(write_only=True,    required=False)
    volume_unit_data    = VolumeUnitSerializer(write_only=True,    required=False)
    area_unit_data      = AreaUnitSerializer(write_only=True,      required=False)
    count_unit_data     = CountUnitSerializer(write_only=True,     required=False)

    class Meta:
        model = Product
        fields = [
            "id", "name", "sale_price", "shelf_code", "category", "category_detail", "unit_type",
            "dimension_unit", "dimension_unit_detail", "dimension_unit_data",
            "weight_unit",    "weight_unit_detail",    "weight_unit_data",
            "volume_unit",    "volume_unit_detail",    "volume_unit_data",
            "area_unit",      "area_unit_detail",      "area_unit_data",
            "count_unit",     "count_unit_detail",     "count_unit_data",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "dimension_unit", "weight_unit", "volume_unit", "area_unit", "count_unit",
        ]

    def validate_shelf_code(self, value):
        return (value or "").strip()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key in UNIT_MAP:
            if key != instance.unit_type:
                data.pop(f"{key}_unit_detail", None)
                data.pop(f"{key}_unit", None)
        return data

    def create(self, validated_data):
        unit_type = validated_data["unit_type"]
        input_field, fk_field, UnitModel, _ = UNIT_MAP[unit_type]
        unit_data = validated_data.pop(input_field, None)
        if unit_data is None:
            raise serializers.ValidationError({input_field: "این فیلد الزامی است."})
        validated_data[fk_field] = UnitModel.objects.create(**unit_data)
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        unit_type = validated_data.get("unit_type", instance.unit_type)
        input_field, fk_field, UnitModel, _ = UNIT_MAP[unit_type]
        unit_data = validated_data.pop(input_field, None)
        if unit_data:
            unit_obj = getattr(instance, fk_field, None)
            if unit_obj:
                for attr, value in unit_data.items():
                    setattr(unit_obj, attr, value)
                unit_obj.save()
            else:
                validated_data[fk_field] = UnitModel.objects.create(**unit_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductInitSerializer(serializers.Serializer):
    name       = serializers.CharField(max_length=255)
    sale_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    category   = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    unit_type  = serializers.ChoiceField(choices=Product.unit_type.field.choices)
    shelf_code = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")

    def validate_shelf_code(self, value):
        return (value or "").strip()


class ProductShelfSerializer(serializers.Serializer):
    """لیست کدهای قفسه همراه با تعداد کالاهای هر قفسه."""
    shelf_code = serializers.CharField()
    product_count = serializers.IntegerField()


class ProductPickSerializer(serializers.ModelSerializer):
    """
    آیتم لیست انتخاب کالا (چک‌لیست فاکتور) برای فرانت.
    موجودی و وضعیت «قبلاً در فاکتور» از context می‌آید (stock_map / order_map).
    """
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    unit_label = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    in_order = serializers.SerializerMethodField()
    ordered_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "shelf_code", "sale_price",
            "category", "category_name",
            "unit_type", "unit_label",
            "current_stock",
            "in_order", "ordered_quantity",
        ]

    def get_unit_label(self, obj):
        return obj.get_unit_type_display() if obj.unit_type else None

    def get_current_stock(self, obj):
        stock_map = self.context.get("stock_map")
        if stock_map is None:
            return None
        return stock_map.get(obj.pk, 0)

    def get_in_order(self, obj):
        order_map = self.context.get("order_map")
        if order_map is None:
            return False
        return obj.pk in order_map

    def get_ordered_quantity(self, obj):
        order_map = self.context.get("order_map")
        if order_map is None:
            return None
        return order_map.get(obj.pk)
