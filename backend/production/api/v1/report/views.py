from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import ProductionPermission
from production.services.report import ProductionReportService

from .serializers import MonthlyReportQuerySerializer


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
