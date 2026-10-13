from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.api.v1.warehouse_staff.serializers import WarehouseStaffSerializer
from access.permissions import WarehousePermission


class WarehouseStaffListView(ListAPIView):
    queryset = WarehouseStaff.objects.select_related("employee").all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [IsAuthenticated]


class WarehouseStaffCreateView(CreateAPIView):
    queryset = WarehouseStaff.objects.all()
    serializer_class = WarehouseStaffSerializer
    permission_classes = [WarehousePermission]


class WarehouseStaffRetrieveView(RetrieveAPIView):
    queryset = WarehouseStaff.objects.select_related("employee").all()
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
