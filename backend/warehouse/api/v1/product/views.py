from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework import status
from rest_framework.response import Response

from warehouse.models.product import Product, ProductCategory
from warehouse.api.v1.product.serializers import ProductSerializer, ProductCategorySerializer, ProductInitSerializer
from access.permissions import WarehousePermission



class ProductCategoryListView(ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


class ProductCategoryCreateView(CreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


class ProductCategoryRetrieveView(RetrieveAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


class ProductCategoryUpdateView(UpdateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


class ProductCategoryDeleteView(DestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]



class ProductListView(ListAPIView):
    queryset = Product.objects.select_related(
        "category", "dimension_unit", "weight_unit",
        "volume_unit", "area_unit", "count_unit"
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [WarehousePermission]


class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [WarehousePermission]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductRetrieveView(RetrieveAPIView):
    queryset = Product.objects.select_related(
        "category", "dimension_unit", "weight_unit",
        "volume_unit", "area_unit", "count_unit"
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [WarehousePermission]


class ProductUpdateView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [WarehousePermission]


class ProductDeleteView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [WarehousePermission]


UNIT_SCHEMAS = {
    "dimension": {"dimension_unit": {"meter": 0, "centimeter": 0, "inch": 0}},
    "weight": {"weight_unit": {"gram": 0, "kilogram": 0, "milligram": 0, "ton": 0}},
    "volume": {"volume_unit": {"liter": 0, "milliliter": 0, "gallon": 0}},
    "area": {"area_unit": {"square_meter": 0, "square_centimeter": 0}},
    "count": {"count_unit": {"quantity_per_unit": 0}},
}
class ProductInitView(CreateAPIView):
    serializer_class = ProductInitSerializer
    permission_classes = [WarehousePermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        unit_schema = UNIT_SCHEMAS[data["unit_type"]]
        unit_key, unit_value = next(iter(unit_schema.items()))

        return Response({
            "name": data["name"],
            "sale_price": data["sale_price"],
            "category": data["category"].id,
            "unit_type": data["unit_type"],
            f"{unit_key}_data": unit_value,
        }, status=status.HTTP_200_OK)

