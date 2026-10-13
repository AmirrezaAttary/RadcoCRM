from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from access.permissions import WarehousePermission

from warehouse.models.warehouse_order_task import (
    OrderTask,
    OrderTaskDeadline,
    OrderTaskAttachment,
)

from warehouse.api.v1.warehouse_order_task.serializers import (
    OrderTaskSerializer,
    OrderTaskCreateSerializer,
    OrderTaskUpdateSerializer,
    OrderTaskDeadlineSerializer,
    OrderTaskAttachmentListSerializer,
    OrderTaskAttachmentCreateSerializer,
    OrderTaskAttachmentDetailSerializer,
    OrderTaskAttachmentUpdateSerializer,
)

from warehouse.services.warehouse_order_task import (
    OrderTaskService,
)


def order_task_queryset():

    return (
        OrderTask.objects
        .select_related(
            "task",
            "warehouse",

            "product",

            "case",
            "case__customer",
            "department",
            "current_step",
            "created_by",

            "performed_by",
            "performed_by__employee",

            "deadline",
        )
        .prefetch_related(
            "assigned_employee",

            "attachments",
            "attachments__performed_by",
            "attachments__performed_by__employee",

            "items",
            "items__product",
            "items__stock_transaction",
        )
    )


class OrderTaskCreateView(
    generics.CreateAPIView
):

    queryset = OrderTask.objects.all()

    serializer_class = OrderTaskCreateSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

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

        order_task = OrderTaskService.create(
            task=serializer.validated_data["task"],

            warehouse=serializer.validated_data[
                "warehouse"
            ],

            items=serializer.validated_data[
                "items"
            ],

            note=serializer.validated_data.get(
                "note",
                "",
            ),

            file=serializer.validated_data.get(
                "file"
            ),

            started_at=serializer.validated_data.get(
                "started_at"
            ),

            deadline=serializer.validated_data.get(
                "deadline"
            ),
        )

        order_task = (
            order_task_queryset()
            .get(pk=order_task.pk)
        )

        response_serializer = OrderTaskSerializer(
            order_task
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderTaskListView(
    generics.ListAPIView
):

    serializer_class = OrderTaskSerializer

    queryset = (
        order_task_queryset()
        .order_by("-created_at")
    )

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskUpdateView(
    generics.UpdateAPIView
):

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    queryset = order_task_queryset()

    serializer_class = OrderTaskUpdateSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        partial = kwargs.pop(
            "partial",
            False,
        )

        order_task = self.get_object()

        serializer = self.get_serializer(
            order_task,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        order_task = OrderTaskService.update(
            order_task=order_task,
            **serializer.validated_data,
        )

        order_task = (
            order_task_queryset()
            .get(pk=order_task.pk)
        )

        response_serializer = OrderTaskSerializer(
            order_task
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class OrderTaskDetailView(
    generics.RetrieveAPIView
):

    queryset = order_task_queryset()

    serializer_class = OrderTaskSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskDeadlineListView(
    generics.ListAPIView
):

    queryset = (
        OrderTaskDeadline.objects
        .select_related(
            "order_task",
            "order_task__warehouse",
        )
        .order_by("-deadline")
    )

    serializer_class = OrderTaskDeadlineSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskDeadlineDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        OrderTaskDeadline.objects
        .select_related(
            "order_task",
            "order_task__warehouse",
        )
    )

    serializer_class = OrderTaskDeadlineSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskAttachmentListView(
    generics.ListAPIView
):

    queryset = (
        OrderTaskAttachment.objects
        .select_related(
            "order_task",
            "order_task__warehouse",

            "performed_by",
            "performed_by__employee",
        )
        .order_by("-created_at")
    )

    serializer_class = OrderTaskAttachmentListSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskAttachmentCreateView(
    generics.CreateAPIView
):

    queryset = OrderTaskAttachment.objects.all()

    serializer_class = (
        OrderTaskAttachmentCreateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskAttachmentDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        OrderTaskAttachment.objects
        .select_related(
            "order_task",
            "order_task__warehouse",

            "performed_by",
            "performed_by__employee",
        )
    )

    serializer_class = (
        OrderTaskAttachmentDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskAttachmentUpdateView(
    generics.UpdateAPIView
):

    queryset = (
        OrderTaskAttachment.objects
        .select_related(
            "order_task",
            "order_task__warehouse",

            "performed_by",
            "performed_by__employee",
        )
    )

    serializer_class = (
        OrderTaskAttachmentUpdateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class OrderTaskAttachmentDeleteView(
    generics.DestroyAPIView
):

    queryset = OrderTaskAttachment.objects.all()

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )