from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import CasePermission
from tasks.models import Case
from tasks.services.case_report import CaseReportService

from .serializers import CaseReportQuerySerializer


@extend_schema(
    parameters=[CaseReportQuerySerializer],
    responses=OpenApiTypes.OBJECT,
)
class CaseReportApi(generics.GenericAPIView):

    queryset = Case.objects.select_related(
        "customer",
        "created_by",
        "created_by__employee_profile",
    ).prefetch_related("resources")

    serializer_class = CaseReportQuerySerializer

    permission_classes = (
        IsAuthenticated,
        CasePermission,
    )

    pagination_class = None
    filter_backends = ()

    def get(self, request, pk):
        case = self.get_object()  # شامل بررسی دسترسی به پرونده

        query = self.get_serializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        data = CaseReportService.build(case=case, request=request)

        sections = query.validated_data.get("sections")
        if sections:
            data = {
                "generated_at": data["generated_at"],
                **{k: data[k] for k in sections},
            }

        return Response(data)
