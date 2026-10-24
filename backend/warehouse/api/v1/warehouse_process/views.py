from django.db.models import Prefetch

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from rest_framework.permissions import (
    IsAuthenticated,
)

from warehouse.models.warehouse_process import (
    InventoryStock,
    StockTransaction,
)


from warehouse.models.product import Product
from warehouse.models.warehouse import Warehouse
from warehouse.models.warehouse_stock_out import (
    WarehouseStockOut,
    WarehouseStockOutItem,
)

from warehouse.services.warehouse_process import (
    InventoryService,
)

from warehouse.services.warehouse_stock_out import (
    WarehouseStockOutService,
)

from warehouse.api.v1.warehouse_process.serializers import (
    InventoryStockSerializer,
    StockTransactionSerializer,
    StockInSerializer,
    StockOutSerializer,
    InitialStockSerializer,
    WarehouseStockOutSerializer,
    InventoryStockLimitSerializer,
)

from access.permissions import WarehousePermission



def inventory_stock_queryset():

    return (
        InventoryStock.objects
        .select_related(
            "warehouse",
            "product",
        )
        .prefetch_related(
            Prefetch(
                "product__transactions",
                queryset=(
                    StockTransaction.objects
                    .filter(
                        transaction_type=(
                            StockTransaction
                            .TransactionType
                            .INITIAL
                        )
                    )
                    .select_related(
                        "warehouse",
                        "performed_by__employee",
                    )
                    .order_by("created_at")
                ),
                to_attr="initial_transactions",
            )
        )
    )


class InventoryStockListView(
    generics.ListAPIView
):

    search_fields = (
        "product__name",
        "product__shelf_code",
        "warehouse__name",
        "warehouse__code",
    )

    serializer_class = InventoryStockSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        queryset = inventory_stock_queryset()

        warehouse_id = (
            self.request
            .query_params
            .get("warehouse_id")
        )

        product_id = (
            self.request
            .query_params
            .get("product_id")
        )

        if warehouse_id:

            queryset = queryset.filter(
                warehouse_id=warehouse_id
            )

        if product_id:

            queryset = queryset.filter(
                product_id=product_id
            )

        return queryset


class InventoryStockRetrieveView(
    generics.RetrieveAPIView
):

    serializer_class = InventoryStockSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return inventory_stock_queryset()


class StockTransactionListView(
    generics.ListAPIView
):

    search_fields = (
        "product__name",
        "product__shelf_code",
        "warehouse__name",
        "note",
        "performed_by__employee__full_name",
    )

    serializer_class = StockTransactionSerializer

    permission_classes = [
        WarehousePermission,
    ]

    def get_queryset(self):

        queryset = (
            StockTransaction.objects
            .select_related(
                "warehouse",
                "product",
                "performed_by__employee",
            )
        )

        warehouse_id = (
            self.request
            .query_params
            .get("warehouse_id")
        )

        product_id = (
            self.request
            .query_params
            .get("product_id")
        )

        transaction_type = (
            self.request
            .query_params
            .get("transaction_type")
        )

        if warehouse_id:

            queryset = queryset.filter(
                warehouse_id=warehouse_id
            )

        if product_id:

            queryset = queryset.filter(
                product_id=product_id
            )

        if transaction_type:

            queryset = queryset.filter(
                transaction_type=transaction_type
            )

        return queryset


class StockTransactionRetrieveView(
    generics.RetrieveAPIView
):

    serializer_class = StockTransactionSerializer

    permission_classes = [
        WarehousePermission,
    ]

    queryset = (
        StockTransaction.objects
        .select_related(
            "warehouse",
            "product",
            "performed_by__employee",
        )
    )


class InitialStockCreateView(
    generics.CreateAPIView
):

    serializer_class = InitialStockSerializer

    permission_classes = [
        WarehousePermission,
    ]

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:

            warehouse = Warehouse.objects.get(
                pk=data["warehouse_id"]
            )

        except Warehouse.DoesNotExist:

            return Response(
                {
                    "detail": "انبار یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            product = Product.objects.get(
                pk=data["product_id"]
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "detail": "کالا یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            stock = (
                InventoryService
                .add_initial_stock(
                    warehouse=warehouse,
                    product=product,
                    quantity=data["quantity"],
                    minimum_stock=data[
                        "minimum_stock"
                    ],
                    maximum_stock=data[
                        "maximum_stock"
                    ],
                    performed_by_id=data[
                        "performed_by_id"
                    ],
                )
            )

        except ValueError as e:

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock = (
            inventory_stock_queryset()
            .get(pk=stock.pk)
        )

        return Response(
            InventoryStockSerializer(
                stock
            ).data,
            status=status.HTTP_201_CREATED,
        )


class StockInView(
    generics.CreateAPIView
):

    serializer_class = StockInSerializer

    permission_classes = [
        WarehousePermission,
    ]

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:

            warehouse = Warehouse.objects.get(
                pk=data["warehouse_id"]
            )

        except Warehouse.DoesNotExist:

            return Response(
                {
                    "detail": "انبار یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            product = Product.objects.get(
                pk=data["product_id"]
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "detail": "کالا یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            transaction_obj = (
                InventoryService
                .stock_in(
                    warehouse=warehouse,
                    product=product,
                    quantity=data["quantity"],
                    performed_by_id=data[
                        "performed_by_id"
                    ],
                    note=data["note"],
                )
            )

        except ValueError as e:

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction_obj = (
            StockTransaction.objects
            .select_related(
                "warehouse",
                "product",
                "performed_by__employee",
            )
            .get(pk=transaction_obj.pk)
        )

        return Response(
            StockTransactionSerializer(
                transaction_obj
            ).data,
            status=status.HTTP_201_CREATED,
        )



@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "warehouse_id": {
                    "type": "integer",
                },
                "performed_by_id": {
                    "type": "integer",
                },
                "note": {
                    "type": "string",
                },
                "file": {
                    "type": "string",
                    "format": "binary",
                },
                "items": {
                    "type": "string",
                    "description": (
                        "JSON array of stock-out items. "
                        "Example: "
                        '[{"product_id":1,"quantity":10,"reason":"sale"}]'
                    ),
                },
            },
            "required": [
                "warehouse_id",
                "performed_by_id",
                "items",
            ],
        },
    },
    responses=WarehouseStockOutSerializer,
)
class StockOutView(
    generics.CreateAPIView
):

    serializer_class = StockOutSerializer

    permission_classes = [
        WarehousePermission,
    ]

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:

            stock_out = (
                WarehouseStockOutService
                .create_stock_out(
                    warehouse_id=data[
                        "warehouse_id"
                    ],
                    performed_by_id=data[
                        "performed_by_id"
                    ],
                    items=data[
                        "items"
                    ],
                    note=data.get(
                        "note",
                        "",
                    ),
                    file=data.get(
                        "file"
                    ),
                )
            )

        except ValueError as e:

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        stock_out = (
            WarehouseStockOut.objects
            .select_related(
                "warehouse",
                "performed_by__employee",
            )
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=(
                        stock_out_item_queryset()
                    ),
                )
            )
            .get(
                pk=stock_out.pk
            )
        )

        return Response(
            WarehouseStockOutSerializer(
                stock_out
            ).data,
            status=status.HTTP_201_CREATED,
        )


def stock_out_item_queryset():

    return (
        WarehouseStockOutItem.objects
        .select_related(
            "product",
            "stock_transaction",
        )
        .order_by("id")
    )
    
class InventoryStockLimitUpdateView(
    generics.UpdateAPIView
):

    serializer_class = InventoryStockLimitSerializer

    permission_classes = [
        WarehousePermission,
    ]

    queryset = (
        InventoryStock.objects
        .select_related(
            "warehouse",
            "product",
        )
    )

    lookup_url_kwarg = "stock_id"

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        partial = kwargs.pop(
            "partial",
            False
        )

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        instance = (
            InventoryStock.objects
            .select_related(
                "warehouse",
                "product",
            )
            .get(
                pk=instance.pk
            )
        )

        return Response(
            InventoryStockSerializer(
                instance
            ).data,
            status=status.HTTP_200_OK,
        )