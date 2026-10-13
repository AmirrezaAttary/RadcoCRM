from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from accounts.models import Employee
from access.models import EmployeePermission

from access.api.v1.serializers.employee_permission import (
    EmployeePermissionListSerializer,
    EmployeePermissionCreateSerializer,
)


class EmployeePermissionListCreateApi(
    generics.ListCreateAPIView,
):
    permission_classes = (
        IsAdminUser,
    )

    def get_queryset(self):

        employee_id = self.kwargs["employee_id"]

        get_object_or_404(
            Employee,
            pk=employee_id,
        )

        return (
            EmployeePermission.objects
            .filter(
                employee_id=employee_id,
                is_active=True,
                permission__is_active=True,
            )
            .select_related(
                "permission",
            )
            .order_by(
                "permission__resource",
                "permission__action",
            )
        )

    def get_serializer_class(self):

        if self.request.method == "POST":
            return EmployeePermissionCreateSerializer

        return EmployeePermissionListSerializer

    def create(self, request, *args, **kwargs):

        employee_id = self.kwargs["employee_id"]

        employee = get_object_or_404(
            Employee,
            pk=employee_id,
        )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        permission = serializer.validated_data["permission"]

        employee_permission, created = (
            EmployeePermission.objects.get_or_create(
                employee=employee,
                permission=permission,
                defaults={
                    "is_active": True,
                },
            )
        )

        if not created and not employee_permission.is_active:

            employee_permission.is_active = True

            employee_permission.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ],
            )

        output_serializer = EmployeePermissionListSerializer(
            employee_permission,
        )

        return Response(
            output_serializer.data,
            status=201 if created else 200,
        )


class EmployeePermissionDeleteApi(
    generics.DestroyAPIView,
):
    permission_classes = (
        IsAdminUser,
    )

    def get_object(self):

        employee_id = self.kwargs["employee_id"]

        permission_code = self.kwargs["permission_code"]

        return get_object_or_404(
            EmployeePermission,
            employee_id=employee_id,
            permission__code=permission_code,
            is_active=True,
        )

    def perform_destroy(self, instance):

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ],
        )