from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.authorization.drf import HasPermission

from department.models import DepartmentEmployee

from tasks.services.tasks import (
    activate_department_employee,
    deactivate_department_employee,
)

from .serializer import (
    DepartmentEmployeeActivateSerializer,
    DepartmentEmployeeCreateSerializer,
    DepartmentEmployeeDeactivateSerializer,
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

    required_permission = "department_employees.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
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

    required_permission = "department_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentEmployeeDeleteApi(generics.DestroyAPIView):

    queryset = DepartmentEmployee.objects.all()

    required_permission = "department_employees.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )
    
class DepartmentEmployeeDeactivateApi(generics.GenericAPIView):

    serializer_class = DepartmentEmployeeDeactivateSerializer

    required_permission = "department_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def post(self, request, department_id, employee_id):

        department_employee = deactivate_department_employee(
            department_id=department_id,
            employee_id=employee_id,
        )

        serializer = self.get_serializer(
            department_employee
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class DepartmentEmployeeActivateApi(generics.GenericAPIView):

    serializer_class = DepartmentEmployeeActivateSerializer

    required_permission = "department_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def post(self, request, department_id, employee_id):

        department_employee = activate_department_employee(
            department_id=department_id,
            employee_id=employee_id,
        )

        serializer = self.get_serializer(
            department_employee
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )