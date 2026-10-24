from django.db.models import Count, Q
from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from warehouse.models.product import Product, ProductCategory
from warehouse.models.warehouse_order_task import OrderTask
from warehouse.models.warehouse_process import InventoryStock
from warehouse.api.v1.product.serializers import (
    ProductSerializer, ProductCategorySerializer, ProductInitSerializer,
    ProductPickSerializer, ProductShelfSerializer,
)
from access.permissions import WarehousePermission


# ── ProductCategory ──────────────────────────────────────────

class ProductCategoryListView(ListAPIView):
    search_fields = (
        "name",
    )

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class ProductCategoryCreateView(CreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class ProductCategoryRetrieveView(RetrieveAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]


class ProductCategoryUpdateView(UpdateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


class ProductCategoryDeleteView(DestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [WarehousePermission]


# ── Product ──────────────────────────────────────────────────

def _filter_products(queryset, params):
    """فیلترهای مشترک: ?shelf_code= ، ?category= ، ?search="""
    shelf_code = (params.get("shelf_code") or "").strip()
    if shelf_code:
        queryset = queryset.filter(shelf_code__iexact=shelf_code)

    category = params.get("category")
    if category:
        if not str(category).isdigit():
            raise serializers.ValidationError({"category": "شناسه دسته‌بندی نامعتبر است."})
        queryset = queryset.filter(category_id=int(category))

    search = (params.get("search") or "").strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(shelf_code__icontains=search)
        )
    return queryset


class ProductListView(ListAPIView):
    queryset = Product.objects.select_related(
        "category", "dimension_unit", "weight_unit",
        "volume_unit", "area_unit", "count_unit"
    ).order_by("shelf_code", "name")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return _filter_products(super().get_queryset(), self.request.query_params)


class ProductShelfListView(ListAPIView):
    """لیست کدهای قفسه + تعداد کالای هر قفسه (برای فیلتر در فرانت)."""
    serializer_class = ProductShelfSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return (
            Product.objects
            .exclude(shelf_code="")
            .values("shelf_code")
            .annotate(product_count=Count("id"))
            .order_by("shelf_code")
        )


class ProductPickListView(ListAPIView):
    """
    لیست کالاها به‌صورت چک‌لیست برای افزودن به فاکتور مشتری.

    query params (همه اختیاری):
      warehouse_id  → موجودی هر کالا در آن انبار (current_stock)
      in_stock=true → فقط کالاهای دارای موجودی (نیازمند warehouse_id)
      order_task_id → علامت‌گذاری کالاهای موجود در این فاکتور (in_order / ordered_quantity)
      shelf_code، category، search → فیلتر
    """
    serializer_class = ProductPickSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _int_param(params, name):
        raw = params.get(name)
        if raw in (None, ""):
            return None
        if not str(raw).isdigit():
            raise serializers.ValidationError({name: "مقدار نامعتبر است."})
        return int(raw)

    def _context_maps(self):
        if hasattr(self, "_maps"):
            return self._maps
        params = self.request.query_params
        stock_map = None
        order_map = None

        warehouse_id = self._int_param(params, "warehouse_id")
        if warehouse_id is not None:
            stock_map = dict(
                InventoryStock.objects
                .filter(warehouse_id=warehouse_id)
                .values_list("product_id", "current_quantity")
            )

        order_task_id = self._int_param(params, "order_task_id")
        if order_task_id is not None:
            order_map = dict(
                OrderTask.objects
                .filter(pk=order_task_id)
                .values_list("items__product_id", "items__quantity")
            )
            order_map.pop(None, None)

        self._maps = (stock_map, order_map)
        return self._maps

    def get_queryset(self):
        params = self.request.query_params
        queryset = Product.objects.select_related("category").order_by("shelf_code", "name")
        queryset = _filter_products(queryset, params)

        stock_map, _ = self._context_maps()
        if str(params.get("in_stock", "")).lower() in ("1", "true", "yes"):
            if stock_map is None:
                raise serializers.ValidationError(
                    {"warehouse_id": "برای فیلتر موجودی، warehouse_id الزامی است."}
                )
            queryset = queryset.filter(
                pk__in=[pk for pk, qty in stock_map.items() if qty and qty > 0]
            )
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        stock_map, order_map = self._context_maps()
        context["stock_map"] = stock_map
        context["order_map"] = order_map
        return context


class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAuthenticated]

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
            "shelf_code": data.get("shelf_code", ""),
            f"{unit_key}_data": unit_value,
        }, status=status.HTTP_200_OK)

