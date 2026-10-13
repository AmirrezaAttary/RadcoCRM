from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from access.authorization.drf import HasPermission
from access.department_step import DepartmentStepAccess

from department.models.department_step import DepartmentStep
from tasks.services.tasks import (
    activate_department_step,
    deactivate_department_step,
)

from .serializer import (
    DepartmentStepListSerializer,
    DepartmentStepCreateSerializer,
    DepartmentStepUpdateSerializer,
    DepartmentStepDetailSerializer,
)


class DepartmentStepListApi(generics.ListAPIView):

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

    required_permission = "department_steps.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentStepDetailApi(generics.RetrieveAPIView):

    serializer_class = DepartmentStepDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):

        return DepartmentStepAccess.get_queryset(
            self.request.user,
        )


class DepartmentStepUpdateApi(generics.UpdateAPIView):

    queryset = DepartmentStep.objects.all()

    serializer_class = DepartmentStepUpdateSerializer

    required_permission = "department_steps.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentStepDeleteApi(generics.DestroyAPIView):

    queryset = DepartmentStep.objects.all()

    required_permission = "department_steps.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class DepartmentStepActivateApi(generics.GenericAPIView):

    queryset = DepartmentStep.objects.all()

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):

        department_step = self.get_object()

        department_step = activate_department_step(
            department_step=department_step,
        )

        return Response(
            DepartmentStepDetailSerializer(
                department_step
            ).data
        )


class DepartmentStepDeactivateApi(generics.GenericAPIView):

    queryset = DepartmentStep.objects.all()

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):

        department_step = self.get_object()

        department_step = deactivate_department_step(
            department_step=department_step,
        )

        return Response(
            DepartmentStepDetailSerializer(
                department_step
            ).data
        )