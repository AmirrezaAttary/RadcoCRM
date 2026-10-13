from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)

from rest_framework.permissions import IsAuthenticated

from access.authorization.drf import HasPermission

from warehouse.models.warehouse_staff import WarehouseStaff

from warehouse.api.v1.warehouse_staff.serializers import (
    WarehouseStaffSerializer,
)


class WarehouseStaffListView(
    ListAPIView
):

    queryset = (
        WarehouseStaff.objects
        .select_related("employee")
        .all()
    )

    serializer_class = WarehouseStaffSerializer

    permission_classes = (
        IsAuthenticated,
    )


class WarehouseStaffCreateView(
    CreateAPIView
):

    queryset = WarehouseStaff.objects.all()

    serializer_class = WarehouseStaffSerializer

    required_permission = "warehouse_staff.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class WarehouseStaffRetrieveView(
    RetrieveAPIView
):

    queryset = (
        WarehouseStaff.objects
        .select_related("employee")
        .all()
    )

    serializer_class = WarehouseStaffSerializer

    permission_classes = (
        IsAuthenticated,
    )


class WarehouseStaffUpdateView(
    UpdateAPIView
):

    queryset = WarehouseStaff.objects.all()

    serializer_class = WarehouseStaffSerializer

    required_permission = "warehouse_staff.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class WarehouseStaffDeleteView(
    DestroyAPIView
):

    queryset = WarehouseStaff.objects.all()

    serializer_class = WarehouseStaffSerializer

    required_permission = "warehouse_staff.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )