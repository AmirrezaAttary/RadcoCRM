from rest_framework import generics
from rest_framework import serializers as drf_serializers
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from access.permissions import WarehousePermission
from warehouse.services.warehouse_scope import scope_by_warehouse

from warehouse.models.warehouse_order_task import (
    OrderTask,
    OrderTaskDeadline,
    OrderTaskAttachment,
)

from warehouse.api.v1.warehouse_order_task.serializers import (
    OrderTaskSerializer,
    OrderTaskCreateSerializer,
    OrderTaskUpdateSerializer,
    OrderTaskConfirmSerializer,
    OrderTaskAddItemsSerializer,
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

    search_fields = (
        "title",
        "description",
        "note",
        "warehouse__name",
        "warehouse__code",
        "product__name",
    )

    serializer_class = OrderTaskSerializer

    queryset = (
        order_task_queryset()
        .order_by("-created_at")
    )

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def get_queryset(self):
        """
        فیلترهای اختیاری (برای صف کار انباردار):
          status        → in_progress / completed / cancelled
          warehouse_id  → فقط سفارش‌های همین انبار
          staff_id      → فقط سفارش‌های انبارهایی که این انباردار به آن‌ها دسترسی دارد
        """

        queryset = scope_by_warehouse(
            super().get_queryset(),
            self.request,
        )

        params = self.request.query_params

        status_param = params.get("status")

        if status_param:

            if status_param not in OrderTask.Status.values:
                raise drf_serializers.ValidationError(
                    {"status": "وضعیت واردشده معتبر نیست."}
                )

            queryset = queryset.filter(status=status_param)

        for name, lookup in (
            ("staff_id", "warehouse__staff_members__pk"),
        ):

            raw = params.get(name)

            if raw in (None, ""):
                continue

            if not str(raw).isdigit():
                raise drf_serializers.ValidationError(
                    {name: "مقدار نامعتبر است."}
                )

            queryset = queryset.filter(**{lookup: int(raw)})

        return queryset


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


class OrderTaskConfirmView(
    generics.GenericAPIView
):
    """
    POST /order_task/<pk>/confirm/
    دکمه «تایید» انباردار روی لیست سفارش مشتری.

    فرم‌دیتا:
      performed_by  → id انباردار (الزامی)
      items         → اختیاری، JSON: [{"product_id": 3, "quantity": 2}]
                      ارسال نشود = همه اقلام به تعداد سفارش تایید می‌شوند
      note، file    → اختیاری
    """

    queryset = order_task_queryset()

    serializer_class = OrderTaskConfirmSerializer

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        order_task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            OrderTaskService.confirm(
                order_task=order_task,
                performed_by=serializer.validated_data[
                    "performed_by"
                ],
                items=serializer.validated_data.get(
                    "items"
                ),
                note=serializer.validated_data.get(
                    "note",
                    "",
                ),
                file=serializer.validated_data.get(
                    "file"
                ),
            )

        except ValueError as exc:
            raise drf_serializers.ValidationError(
                {"detail": str(exc)}
            )

        order_task = (
            order_task_queryset()
            .get(pk=order_task.pk)
        )

        return Response(
            OrderTaskSerializer(order_task).data,
            status=status.HTTP_200_OK,
        )


class OrderTaskAddItemsView(
    generics.GenericAPIView
):
    """
    POST /order_task/<pk>/add-items/
    افزودن کالاهای تیک‌خورده به فاکتور مشتری.
    """

    queryset = order_task_queryset()

    serializer_class = OrderTaskAddItemsSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        order_task = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            OrderTaskService.add_items(
                order_task=order_task,
                items=serializer.validated_data[
                    "items"
                ],
            )

        except ValueError as exc:
            raise drf_serializers.ValidationError(
                {"detail": str(exc)}
            )

        order_task = (
            order_task_queryset()
            .get(pk=order_task.pk)
        )

        return Response(
            OrderTaskSerializer(order_task).data,
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

    search_fields = (
        "order_task__title",
        "order_task__warehouse__name",
    )

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

    def get_queryset(self):
        # انبار از طریق سفارش: order_task__warehouse
        return scope_by_warehouse(
            super().get_queryset(),
            self.request,
            field="order_task__warehouse_id",
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

    search_fields = (
        "note",
        "order_task__title",
        "order_task__warehouse__name",
        "performed_by__employee__full_name",
    )

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

    def get_queryset(self):
        return scope_by_warehouse(
            super().get_queryset(),
            self.request,
            field="order_task__warehouse_id",
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