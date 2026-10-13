from rest_framework import generics

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


class QualityControlEmployeeCreateView(
    generics.CreateAPIView
):
    queryset = QualityControlEmployee.objects.all()
    serializer_class = QualityControlEmployeeSerializer


class QualityControlEmployeeDetailView(
    generics.RetrieveAPIView
):
    queryset = (
        QualityControlEmployee.objects
        .select_related("user")
        .all()
    )
    serializer_class = QualityControlEmployeeSerializer


class QualityControlEmployeeUpdateView(
    generics.UpdateAPIView
):
    queryset = (
        QualityControlEmployee.objects
        .select_related("user")
        .all()
    )
    serializer_class = QualityControlEmployeeSerializer


class QualityControlEmployeeDeleteView(
    generics.DestroyAPIView
):
    queryset = QualityControlEmployee.objects.all()
    serializer_class = QualityControlEmployeeSerializer
