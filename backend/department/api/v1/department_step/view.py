from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from access.department_step import DepartmentStepAccess
from access.permissions import DepartmentStepPermission

from department.models.department_step import DepartmentStep

from .serializer import (
    DepartmentStepListSerializer,
    DepartmentStepCreateSerializer,
    DepartmentStepUpdateSerializer,
    DepartmentStepDetailSerializer,
)


class DepartmentStepListApi(generics.ListAPIView):

    search_fields = (
        "name",
        "description",
        "department__name",
    )

    serializer_class = DepartmentStepListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):

        return DepartmentStepAccess.get_queryset(
            self.request.user,
        )


class DepartmentStepCreateApi(generics.CreateAPIView):

    queryset = DepartmentStep.objects.all()

    serializer_class = DepartmentStepCreateSerializer

    permission_classes = (
        IsAdminUser,
    )


class DepartmentStepDetailApi(generics.RetrieveAPIView):

    queryset = DepartmentStep.objects.all()

    serializer_class = DepartmentStepDetailSerializer

    permission_classes = (
        IsAuthenticated,
        DepartmentStepPermission,
    )


class DepartmentStepUpdateApi(generics.UpdateAPIView):

    queryset = DepartmentStep.objects.all()

    serializer_class = DepartmentStepUpdateSerializer

    permission_classes = (
        IsAuthenticated,
        DepartmentStepPermission,
    )


class DepartmentStepDeleteApi(generics.DestroyAPIView):

    queryset = DepartmentStep.objects.all()

    permission_classes = (
        IsAuthenticated,
        DepartmentStepPermission,
    )