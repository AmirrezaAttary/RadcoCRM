from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.authorization.drf import HasPermission

from quality_control.models.employee import QualityControlEmployee

from .serializers import (
    QualityControlEmployeeSerializer,
)


class QualityControlEmployeeListView(
    generics.ListAPIView
):

    queryset = (
        QualityControlEmployee.objects
        .select_related("user")
        .all()
    )

    serializer_class = QualityControlEmployeeSerializer

    permission_classes = (
        IsAuthenticated,
    )


class QualityControlEmployeeCreateView(
    generics.CreateAPIView
):

    queryset = QualityControlEmployee.objects.all()

    serializer_class = QualityControlEmployeeSerializer

    required_permission = "quality_control_employees.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class QualityControlEmployeeDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        QualityControlEmployee.objects
        .select_related("user")
        .all()
    )

    serializer_class = QualityControlEmployeeSerializer

    permission_classes = (
        IsAuthenticated,
    )


class QualityControlEmployeeUpdateView(
    generics.UpdateAPIView
):

    queryset = (
        QualityControlEmployee.objects
        .select_related("user")
        .all()
    )

    serializer_class = QualityControlEmployeeSerializer

    required_permission = "quality_control_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class QualityControlEmployeeDeleteView(
    generics.DestroyAPIView
):

    queryset = QualityControlEmployee.objects.all()

    serializer_class = QualityControlEmployeeSerializer

    required_permission = "quality_control_employees.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )