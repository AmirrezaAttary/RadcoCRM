from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.api.v1.warehouse_staff.serializers import WarehouseStaffSerializer
from access.permissions import WarehousePermission


class WarehouseStaffListView(ListAPIView):
    search_fields = (
        "employee__full_name",
        "employee__user__username",
    )

    serializer_class = WarehouseStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            WarehouseStaff.objects
            .select_related("employee")
            .prefetch_related("warehouses")
        )

        # فقط انباردارهای یک انبار مشخص: ?warehouse_id=3
        warehouse_id = self.request.query_params.get("warehouse_id")

        if warehouse_id:
            queryset = queryset.filter(warehouses__id=warehouse_id)

        return queryset


class WarehouseStaffCreateView(CreateAPIView):
    queryset = WarehouseStaff.objects.all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [WarehousePermission]


class WarehouseStaffRetrieveView(RetrieveAPIView):
    queryset = (
        WarehouseStaff.objects
        .select_related("employee")
        .prefetch_related("warehouses")
    )
    serializer_class = WarehouseStaffSerializer
    permission_classes = [IsAuthenticated]


class WarehouseStaffUpdateView(UpdateAPIView):
    queryset = WarehouseStaff.objects.all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [WarehousePermission]


class WarehouseStaffDeleteView(DestroyAPIView):
    queryset = WarehouseStaff.objects.all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [WarehousePermission]
