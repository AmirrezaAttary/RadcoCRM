from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from department.models import DepartmentEmployee

from .serializer import (
    DepartmentEmployeeCreateSerializer,
    DepartmentEmployeeListSerializer,
    DepartmentEmployeeUpdateSerializer,
)


class DepartmentEmployeeListApi(generics.ListAPIView):

    queryset = DepartmentEmployee.objects.select_related(
        "employee",
        "department",
    )

    serializer_class = DepartmentEmployeeListSerializer

    permission_classes = (
        IsAuthenticated,
    )


class DepartmentEmployeeCreateApi(generics.CreateAPIView):

    queryset = DepartmentEmployee.objects.all()

    serializer_class = DepartmentEmployeeCreateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class DepartmentEmployeeDetailApi(generics.RetrieveAPIView):

    queryset = DepartmentEmployee.objects.select_related(
        "employee",
        "department",
    )

    serializer_class = DepartmentEmployeeListSerializer

    permission_classes = (
        IsAuthenticated,
    )


class DepartmentEmployeeUpdateApi(generics.UpdateAPIView):

    queryset = DepartmentEmployee.objects.all()

    serializer_class = DepartmentEmployeeUpdateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class DepartmentEmployeeDeleteApi(generics.DestroyAPIView):

    queryset = DepartmentEmployee.objects.all()

    permission_classes = (
        IsAuthenticated,
    )