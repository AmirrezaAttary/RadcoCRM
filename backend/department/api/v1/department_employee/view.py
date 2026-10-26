from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from department.models import DepartmentEmployee

from .serializer import (
    DepartmentEmployeeCreateSerializer,
    DepartmentEmployeeListSerializer,
    DepartmentEmployeeUpdateSerializer,
)


class DepartmentEmployeeListApi(generics.ListAPIView):

    search_fields = (
        "employee__full_name",
        "department__name",
    )

    queryset = DepartmentEmployee.objects.select_related(
        "employee",
        "department",
    )

    serializer_class = DepartmentEmployeeListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        ?department=<id>   → فقط کارمندان یک دپارتمان
        ?employee=<id>     → فقط عضویت‌های یک کارمند
        """
        queryset = super().get_queryset()
        params = self.request.query_params

        department = params.get("department")
        if department and department.isdigit():
            queryset = queryset.filter(department_id=int(department))

        employee = params.get("employee")
        if employee and employee.isdigit():
            queryset = queryset.filter(employee_id=int(employee))

        return queryset


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