from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import ProductionPermission
from production.services.machine_report import MachineReportService
from production.services.report import ProductionReportService
from production.services.variance_report import VarianceReportService

from .serializers import (
    MachineMonthlyQuerySerializer,
    MachineSummaryQuerySerializer,
    MonthlyReportQuerySerializer,
    VarianceQuerySerializer,
)


@extend_schema(
    parameters=[MonthlyReportQuerySerializer],
    responses=OpenApiTypes.OBJECT,
)
class MonthlyProductionReportView(generics.GenericAPIView):

    serializer_class = MonthlyReportQuerySerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def get(self, request):

        serializer = self.get_serializer(
            data=request.query_params
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = ProductionReportService.monthly(
            year=serializer.validated_data["year"],
            month=serializer.validated_data["month"],
            employee_id=serializer.validated_data.get(
                "employee_id"
            ),
        )

        return Response(data)


@extend_schema(
    parameters=[MachineSummaryQuerySerializer],
    responses=OpenApiTypes.OBJECT,
)
class MachineSummaryReportView(generics.GenericAPIView):

    serializer_class = MachineSummaryQuerySerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def get(self, request):

        serializer = self.get_serializer(
            data=request.query_params
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = MachineReportService.summary(
            date_from=serializer.validated_data["date_from"],
            date_to=serializer.validated_data["date_to"],
            group_by=serializer.validated_data["group_by"],
            machine=serializer.validated_data.get("machine_id"),
        )

        return Response(data)


@extend_schema(
    parameters=[MachineMonthlyQuerySerializer],
    responses=OpenApiTypes.OBJECT,
)
class MachineMonthlyReportView(generics.GenericAPIView):

    serializer_class = MachineMonthlyQuerySerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def get(self, request):

        serializer = self.get_serializer(
            data=request.query_params
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = MachineReportService.monthly(
            year=serializer.validated_data["year"],
            month=serializer.validated_data["month"],
            machine=serializer.validated_data.get("machine_id"),
        )

        return Response(data)


@extend_schema(
    parameters=[VarianceQuerySerializer],
    responses=OpenApiTypes.OBJECT,
)
class VarianceReportView(generics.GenericAPIView):
    """
    تفاضل تولید و ضایعات واقعی از استاندارد، برای نمودار؛
    به تفکیک دستگاه و/یا اپراتور و به تفکیک روز/هفته/ماه/سال.
    """

    serializer_class = VarianceQuerySerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    pagination_class = None
    filter_backends = ()

    def get(self, request):

        serializer = self.get_serializer(
            data=request.query_params
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = VarianceReportService.build(
            date_from=serializer.validated_data["date_from"],
            date_to=serializer.validated_data["date_to"],
            group_by=serializer.validated_data["group_by"],
            entity=serializer.validated_data["entity"],
            machine=serializer.validated_data.get("machine_id"),
            employee=serializer.validated_data.get("employee_id"),
        )

        return Response(data)
