from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from access.permissions import PurchasePermission

from purchasing.models.purchase_task import PurchaseTask
from purchasing.services.purchase_service import PurchaseService

from .serializers import (
    PurchaseTaskSerializer,
    PurchaseTaskCreateSerializer,
    PurchaseTaskInitialCreateSerializer,
    PurchaseTaskActionSerializer,
    PurchaseTaskHistorySerializer,
    PurchaseTaskStatusSerializer,
)


class PurchaseTaskListCreateView(generics.ListCreateAPIView):

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    def get_queryset(self):
        return (
            PurchaseTask.objects
            .select_related(
                "warehouse",
                "product",
                "process_step",
                "created_by",
            )
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseTaskCreateSerializer

        return PurchaseTaskSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = PurchaseService.create_manual_purchase_task(
                data=serializer.validated_data,
                created_by=request.user,
            )

        except DjangoValidationError as exc:
            return Response(
                {
                    "detail": exc.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = PurchaseTaskSerializer(
            task,
            context=self.get_serializer_context(),
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseTaskInitialCreateView(generics.GenericAPIView):

    serializer_class = PurchaseTaskInitialCreateSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = PurchaseService.create_initial_purchase_task(
                product=serializer.validated_data["product"],
                quantity=serializer.validated_data["quantity"],
                created_by=request.user,
            )

        except DjangoValidationError as exc:
            return Response(
                {
                    "detail": exc.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = PurchaseTaskSerializer(
            task,
            context=self.get_serializer_context(),
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseTaskDetailView(generics.RetrieveAPIView):

    serializer_class = PurchaseTaskSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    def get_queryset(self):
        return (
            PurchaseTask.objects
            .select_related(
                "warehouse",
                "product",
                "process_step",
                "created_by",
            )
        )


class PurchaseTaskAdvanceView(generics.GenericAPIView):

    queryset = PurchaseTask.objects.all()

    serializer_class = PurchaseTaskActionSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, *args, **kwargs):

        task = get_object_or_404(
            PurchaseTask,
            pk=kwargs["pk"],
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        task, attachment = PurchaseService.advance_task(
            task=task,
            employee=serializer.validated_data["created_by"],
            note=serializer.validated_data.get("note"),
            file=serializer.validated_data.get("file"),
        )

        return Response(
            {
                "detail": "تسک با موفقیت به مرحله بعد منتقل شد.",
                "task_id": task.id,
                "warehouse": task.warehouse_id,
                "product": task.product_id,
                "process_step": task.process_step.title,
                "attachment_id": attachment.id,
            },
            status=status.HTTP_200_OK,
        )


class PurchaseTaskRevertView(generics.GenericAPIView):

    queryset = PurchaseTask.objects.all()

    serializer_class = PurchaseTaskActionSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, *args, **kwargs):

        task = get_object_or_404(
            PurchaseTask,
            pk=kwargs["pk"],
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        task, attachment = PurchaseService.revert_task(
            task=task,
            employee=serializer.validated_data["created_by"],
            note=serializer.validated_data.get("note"),
            file=serializer.validated_data.get("file"),
        )

        return Response(
            {
                "detail": "تسک با موفقیت به مرحله قبل بازگشت.",
                "task_id": task.id,
                "warehouse": task.warehouse_id,
                "product": task.product_id,
                "process_step": task.process_step.title,
                "attachment_id": attachment.id,
            },
            status=status.HTTP_200_OK,
        )


class PurchaseTaskHistoryListView(
    generics.ListAPIView
):

    serializer_class = PurchaseTaskHistorySerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    queryset = (
        PurchaseTask.objects
        .select_related(
            "warehouse",
            "product",
            "process_step",
            "created_by",
        )
        .prefetch_related(
            "attachments",
            "attachments__process_step",
            "attachments__created_by",
            "attachments__created_by__employee",
        )
        .order_by("-created_at")
    )


class PurchaseTaskHistoryDetailView(
    generics.RetrieveAPIView
):

    serializer_class = PurchaseTaskHistorySerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    queryset = (
        PurchaseTask.objects
        .select_related(
            "warehouse",
            "product",
            "process_step",
            "created_by",
        )
        .prefetch_related(
            "attachments",
            "attachments__process_step",
            "attachments__created_by",
            "attachments__created_by__employee",
        )
    )


class PurchaseTaskStatusView(generics.GenericAPIView):

    queryset = (
        PurchaseTask.objects
        .select_related(
            "warehouse",
            "product",
            "process_step",
        )
    )

    serializer_class = PurchaseTaskStatusSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission,
    )

    def patch(self, request, pk):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = PurchaseService.change_status(
                task=task,
                status=serializer.validated_data["status"],
            )

        except DjangoValidationError as exc:
            return Response(
                {
                    "detail": exc.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "وضعیت تسک با موفقیت تغییر کرد.",
                "id": task.id,
                "warehouse": task.warehouse_id,
                "product": task.product_id,
                "status": task.status,
                "status_display": (
                    task.get_status_display()
                ),
                "process_step": (
                    task.process_step.title
                ),
                "process_step_order": (
                    task.process_step.order
                ),
            },
            status=status.HTTP_200_OK,
        )