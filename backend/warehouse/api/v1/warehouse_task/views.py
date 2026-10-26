from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import WarehousePermission
from warehouse.services.warehouse_scope import scope_by_warehouse

from warehouse.models.warehouse import Warehouse
from warehouse.models.warehouse_task import WarehouseTask
from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.services.warehouse_task import WarehouseTaskService

from .serializers import (
    WarehouseTaskSerializer,
    WarehouseTaskCompleteSerializer,
    WarehouseTaskInitialCompleteSerializer,
    WarehouseTaskCancelSerializer,
    WarehouseTaskReopenSerializer,
)


class WarehouseTaskListView(generics.ListAPIView):

    search_fields = (
        "note",
        "product__name",
        "warehouse__name",
        "assigned_to__employee__full_name",
    )

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def get_queryset(self):
        return scope_by_warehouse(
            super().get_queryset(),
            self.request,
        )


class WarehouseTaskDetailView(generics.RetrieveAPIView):

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class WarehouseTaskCompleteView(generics.GenericAPIView):

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskCompleteSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(self, request, pk):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        assigned_to_id = serializer.validated_data[
            "assigned_to"
        ]

        warehouse_staff = (
            WarehouseStaff.objects
            .filter(
                pk=assigned_to_id,
                is_active=True,
            )
            .first()
        )

        if not warehouse_staff:
            return Response(
                {
                    "detail": "انباردار یافت نشد یا فعال نیست."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            task, transaction_obj = (
                WarehouseTaskService.complete_task(
                    task=task,
                    warehouse_staff=warehouse_staff,
                    received_quantity=(
                        serializer.validated_data[
                            "received_quantity"
                        ]
                    ),
                    note=serializer.validated_data.get(
                        "note"
                    ),
                    file=serializer.validated_data.get(
                        "file"
                    ),
                )
            )

        except DjangoValidationError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "تسک انبار با موفقیت تکمیل شد.",
                "warehouse_task": (
                    WarehouseTaskSerializer(
                        task
                    ).data
                ),
                "stock_transaction_id": (
                    transaction_obj.id
                    if transaction_obj
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )


class WarehouseTaskInitialCompleteView(generics.GenericAPIView):

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskInitialCompleteSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(self, request, pk):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        warehouse_id = serializer.validated_data[
            "warehouse"
        ]

        performed_by_id = serializer.validated_data[
            "performed_by_id"
        ]

        warehouse = (
            Warehouse.objects
            .filter(
                pk=warehouse_id,
            )
            .first()
        )

        if not warehouse:
            return Response(
                {
                    "detail": "انبار یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        warehouse_staff = (
            WarehouseStaff.objects
            .filter(
                pk=performed_by_id,
                is_active=True,
            )
            .first()
        )

        if not warehouse_staff:
            return Response(
                {
                    "detail": "انباردار یافت نشد یا فعال نیست."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            task, stock = (
                WarehouseTaskService.complete_initial_task(
                    task=task,
                    warehouse=warehouse,
                    warehouse_staff=warehouse_staff,
                    received_quantity=(
                        serializer.validated_data[
                            "quantity"
                        ]
                    ),
                    minimum_stock=(
                        serializer.validated_data[
                            "minimum_stock"
                        ]
                    ),
                    maximum_stock=(
                        serializer.validated_data[
                            "maximum_stock"
                        ]
                    ),
                    note=serializer.validated_data.get(
                        "note"
                    ),
                    file=serializer.validated_data.get(
                        "file"
                    ),
                )
            )

        except DjangoValidationError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "موجودی اولیه با موفقیت ثبت شد.",
                "warehouse_task": (
                    WarehouseTaskSerializer(
                        task
                    ).data
                ),
                "stock_id": stock.id,
                "stock_quantity": stock.current_quantity,
                "minimum_stock": stock.minimum_stock,
                "maximum_stock": stock.maximum_stock,
            },
            status=status.HTTP_200_OK,
        )


class WarehouseTaskCancelView(generics.GenericAPIView):

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskCancelSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(self, request, pk):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            task = WarehouseTaskService.cancel_task(
                task=task,
                note=serializer.validated_data.get(
                    "note"
                ),
            )

        except DjangoValidationError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "تسک انبار با موفقیت لغو شد.",
                "warehouse_task": (
                    WarehouseTaskSerializer(
                        task
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )


class WarehouseTaskReopenView(generics.GenericAPIView):

    queryset = (
        WarehouseTask.objects
        .select_related(
            "warehouse",
            "product",
            "assigned_to",
            "assigned_to__employee",
            "purchase_task",
            "quality_control",
        )
    )

    serializer_class = WarehouseTaskReopenSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(self, request, pk):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            task = (
                WarehouseTaskService
                .restore_cancelled_task(
                    task=task,
                )
            )

        except DjangoValidationError as exc:

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "تسک انبار با موفقیت مجدداً فعال شد.",
                "warehouse_task": (
                    WarehouseTaskSerializer(
                        task
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )