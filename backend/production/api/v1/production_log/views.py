from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.permissions import ProductionPermission
from production.models.production_log import ProductionLog

from .serializers import ProductionLogSerializer


def _base_queryset():
    return ProductionLog.objects.select_related(
        "employee",
        "employee__user",
        "machine",
    )


class ProductionLogListView(generics.ListAPIView):

    serializer_class = ProductionLogSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def get_queryset(self):
        queryset = _base_queryset()
        params = self.request.query_params

        # ?employee_id=3&machine_id=2&date_from=2026-10-01&date_to=2026-10-31
        employee_id = params.get("employee_id")
        machine_id = params.get("machine_id")
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset


class ProductionLogCreateView(generics.CreateAPIView):

    queryset = ProductionLog.objects.all()
    serializer_class = ProductionLogSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class ProductionLogDetailView(generics.RetrieveAPIView):

    queryset = _base_queryset()
    serializer_class = ProductionLogSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class ProductionLogUpdateView(generics.UpdateAPIView):

    queryset = _base_queryset()
    serializer_class = ProductionLogSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class ProductionLogDeleteView(generics.DestroyAPIView):

    queryset = ProductionLog.objects.all()
    serializer_class = ProductionLogSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )
