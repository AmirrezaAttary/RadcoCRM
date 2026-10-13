from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from access.department import DepartmentAccess
from access.permissions import DepartmentPermission
from access.authorization.drf import HasPermission

from department.models import Department
from tasks.services.tasks import (
    activate_department,
    deactivate_department,
)

from .serializer import (
    DepartmentListSerializer,
    DepartmentCreateSerializer,
    DepartmentUpdateSerializer,
    DepartmentDetailSerializer,
)


class DepartmentListApi(generics.ListAPIView):

    serializer_class = DepartmentListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):

        return DepartmentAccess.get_queryset(
            self.request.user,
        )


class DepartmentCreateApi(generics.CreateAPIView):

    queryset = Department.objects.all()

    serializer_class = DepartmentCreateSerializer

    required_permission = "departments.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentDetailApi(generics.RetrieveAPIView):

    queryset = Department.objects.all()

    serializer_class = DepartmentDetailSerializer

    permission_classes = (
        IsAuthenticated,
        DepartmentPermission,
    )


class DepartmentUpdateApi(generics.UpdateAPIView):

    queryset = Department.objects.all()

    serializer_class = DepartmentUpdateSerializer

    required_permission = "departments.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentDeleteApi(generics.DestroyAPIView):

    queryset = Department.objects.all()

    required_permission = "departments.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentActivateApi(generics.GenericAPIView):

    queryset = Department.objects.all()

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):

        department = self.get_object()

        department = activate_department(
            department=department,
        )

        return Response(
            DepartmentDetailSerializer(
                department
            ).data
        )


class DepartmentDeactivateApi(generics.GenericAPIView):

    queryset = Department.objects.all()

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):

        department = self.get_object()

        department = deactivate_department(
            department=department,
        )

        return Response(
            DepartmentDetailSerializer(
                department
            ).data
        )