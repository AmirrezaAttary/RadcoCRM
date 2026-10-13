from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from access.permissions import QualityControlPermission

from ....models.quality_control import QualityControl

from .serializers import (
    QualityControlSerializer,
    QualityControlActionSerializer,
    QualityControlActivateSerializer,
    QualityControlDeactivateSerializer,
)

from quality_control.models.employee import QualityControlEmployee

from ....services.quality_control import (
    QualityControlService,
)


class QualityControlListView(
    generics.ListAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__warehouse",
            "purchase_task__product",
            "purchase_task__process_step",
            "checked_by",
            "checked_by__user",
        )
    )

    serializer_class = QualityControlSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )


class QualityControlDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__warehouse",
            "purchase_task__product",
            "purchase_task__process_step",
            "checked_by",
            "checked_by__user",
        )
    )

    serializer_class = QualityControlSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )


class QualityControlApproveView(
    generics.GenericAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__warehouse",
            "purchase_task__product",
            "purchase_task__process_step",
        )
    )

    serializer_class = QualityControlActionSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, pk):

        quality_control = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        checked_by = serializer.validated_data[
            "checked_by"
        ]

        # =====================================================
        # Find Active QC Employee
        # =====================================================

        employee = (
            QualityControlEmployee.objects
            .filter(
                pk=checked_by,
                is_active=True,
            )
            .first()
        )

        if not employee:

            return Response(
                {
                    "detail":
                        "کارمند بررسی‌کننده یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # Approve
        # =====================================================

        try:

            quality_control, warehouse_task = (
                QualityControlService.approve(
                    quality_control=quality_control,

                    checked_by=employee,

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
                    "detail": exc.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # Response
        # =====================================================

        return Response(
            {
                "detail":
                    "کنترل کیفیت با موفقیت تایید شد.",

                "quality_control_id":
                    quality_control.id,

                "purchase_task_id":
                    quality_control.purchase_task_id,

                "warehouse_id":
                    warehouse_task.warehouse_id,

                "product_id":
                    warehouse_task.product_id,

                "warehouse_task_id":
                    warehouse_task.id,

                "status":
                    quality_control.status,

                "active":
                    quality_control.active,
            },
            status=status.HTTP_200_OK,
        )


class QualityControlRejectView(
    generics.GenericAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__process_step",
            "purchase_task__warehouse",
            "purchase_task__product",
        )
    )

    serializer_class = QualityControlActionSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request, pk):

        quality_control = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        checked_by = serializer.validated_data[
            "checked_by"
        ]

        # =====================================================
        # Find Active QC Employee
        # =====================================================

        employee = (
            QualityControlEmployee.objects
            .filter(
                pk=checked_by,
                is_active=True,
            )
            .first()
        )

        if not employee:

            return Response(
                {
                    "detail":
                        "کارمند بررسی‌کننده یافت نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =====================================================
        # Reject
        # =====================================================

        try:

            quality_control = (
                QualityControlService.reject(
                    quality_control=quality_control,

                    checked_by=employee,

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
                    "detail": exc.message
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =====================================================
        # Response
        # =====================================================

        purchase_task = (
            quality_control.purchase_task
        )

        return Response(
            {
                "detail":
                    "کنترل کیفیت رد شد و تسک خرید "
                    "به مرحله اول بازگشت.",

                "quality_control_id":
                    quality_control.id,

                "purchase_task_id":
                    quality_control.purchase_task_id,

                "warehouse_id":
                    purchase_task.warehouse_id,

                "product_id":
                    purchase_task.product_id,

                "status":
                    quality_control.status,

                "active":
                    quality_control.active,

                "current_step":
                    purchase_task.process_step.title,

                "current_step_order":
                    purchase_task.process_step.order,
            },
            status=status.HTTP_200_OK,
        )


class QualityControlActivateView(
    generics.GenericAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__warehouse",
            "purchase_task__product",
            "purchase_task__process_step",
            "checked_by",
            "checked_by__user",
        )
    )

    serializer_class = QualityControlActivateSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )

    def post(self, request, pk):

        quality_control = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            quality_control = (
                QualityControlService.activate(
                    quality_control
                )
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
                "detail":
                    "کنترل کیفیت با موفقیت فعال شد.",

                "quality_control":
                    QualityControlSerializer(
                        quality_control
                    ).data,
            },
            status=status.HTTP_200_OK,
        )


class QualityControlDeactivateView(
    generics.GenericAPIView
):

    queryset = (
        QualityControl.objects
        .select_related(
            "purchase_task",
            "purchase_task__warehouse",
            "purchase_task__product",
            "purchase_task__process_step",
            "checked_by",
            "checked_by__user",
        )
    )

    serializer_class = QualityControlDeactivateSerializer

    permission_classes = (
        IsAuthenticated,
        QualityControlPermission,
    )

    def post(self, request, pk):

        quality_control = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            quality_control = (
                QualityControlService.deactivate(
                    quality_control
                )
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
                "detail":
                    "کنترل کیفیت با موفقیت غیرفعال شد.",

                "quality_control":
                    QualityControlSerializer(
                        quality_control
                    ).data,
            },
            status=status.HTTP_200_OK,
        )