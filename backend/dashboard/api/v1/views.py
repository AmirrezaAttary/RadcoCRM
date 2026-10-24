from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import IsAdmin
from dashboard.services.stats import DashboardService

from .serializers import (
    OverviewQuerySerializer,
    PeriodQuerySerializer,
    TopExpertsQuerySerializer,
)


class _BaseDashboardView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = None
    filter_backends = ()

    def _params(self):
        s = self.get_serializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        return s.validated_data


@extend_schema(responses=OpenApiTypes.OBJECT)
class SummaryView(_BaseDashboardView):
    serializer_class = PeriodQuerySerializer

    def get(self, request):
        return Response(DashboardService.summary())


@extend_schema(parameters=[PeriodQuerySerializer], responses=OpenApiTypes.OBJECT)
class SalesChartView(_BaseDashboardView):
    serializer_class = PeriodQuerySerializer

    def get(self, request):
        return Response(DashboardService.sales_chart(self._params()["period"]))


@extend_schema(parameters=[PeriodQuerySerializer], responses=OpenApiTypes.OBJECT)
class CustomerSourcesView(_BaseDashboardView):
    serializer_class = PeriodQuerySerializer

    def get(self, request):
        return Response(DashboardService.customer_sources(self._params()["period"]))


@extend_schema(parameters=[PeriodQuerySerializer], responses=OpenApiTypes.OBJECT)
class CancelledByDepartmentView(_BaseDashboardView):
    serializer_class = PeriodQuerySerializer

    def get(self, request):
        return Response(
            DashboardService.cancelled_by_department(self._params()["period"])
        )


@extend_schema(parameters=[TopExpertsQuerySerializer], responses=OpenApiTypes.OBJECT)
class TopExpertsView(_BaseDashboardView):
    serializer_class = TopExpertsQuerySerializer

    def get(self, request):
        p = self._params()
        return Response(DashboardService.top_experts(p["period"], p["limit"]))


@extend_schema(parameters=[OverviewQuerySerializer], responses=OpenApiTypes.OBJECT)
class OverviewView(_BaseDashboardView):
    serializer_class = OverviewQuerySerializer

    def get(self, request):
        return Response(DashboardService.overview(**self._params()))
