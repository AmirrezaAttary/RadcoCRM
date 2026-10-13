from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from access.department import DepartmentAccess
from access.permissions import DepartmentPermission

from department.models import Department

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

    permission_classes = (
        IsAdminUser,
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

    permission_classes = (
        IsAuthenticated,
        DepartmentPermission,
    )


class DepartmentDeleteApi(generics.DestroyAPIView):

    queryset = Department.objects.all()

    permission_classes = (
        IsAuthenticated,
        DepartmentPermission,
    )