from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.permissions import WarehousePermission

from warehouse.models.warehouse import Warehouse

from .serializers import WarehouseSerializer


class WarehouseListView(
    generics.ListAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class WarehouseCreateView(
    generics.CreateAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class WarehouseRetrieveView(
    generics.RetrieveAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class WarehouseUpdateView(
    generics.UpdateAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    http_method_names = [
        "put",
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )


class WarehousePatchView(
    generics.UpdateAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    http_method_names = [
        "patch",
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(
            request,
            *args,
            **kwargs
        )


class WarehouseDeleteView(
    generics.DestroyAPIView
):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    http_method_names = [
        "delete",
    ]

    permission_classes = (
        IsAuthenticated,
        WarehousePermission,
    )