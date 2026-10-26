from django.db.models import Count, Q

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from access.department import DepartmentAccess
from access.permissions import DepartmentPermission

from department.models import Department

from .serializer import (
    DepartmentListSerializer,
    DepartmentChoiceSerializer,
    DepartmentCreateSerializer,
    DepartmentUpdateSerializer,
    DepartmentDetailSerializer,
)


class DepartmentListApi(generics.ListAPIView):

    search_fields = (
        "name",
        "description",
    )

    serializer_class = DepartmentListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):

        return DepartmentAccess.get_queryset(
            self.request.user,
        )


class DepartmentChoiceListApi(generics.ListAPIView):
    """
    لیست همه‌ی دپارتمان‌ها برای انتخاب مقصد در «انتقال تسک بین دپارتمان‌ها».

    برخلاف /department/list/ که با دسترسی کاربر محدود می‌شود، اینجا همه‌ی
    دپارتمان‌ها می‌آیند، چون مقصد انتقال معمولاً دپارتمانی است که کاربر
    عضو آن نیست.

    query params (اختیاری):
      task_id → دپارتمان فعلی همین تسک از لیست حذف می‌شود
    """

    serializer_class = DepartmentChoiceSerializer

    permission_classes = (
        IsAuthenticated,
    )

    pagination_class = None

    def get_queryset(self):

        queryset = (
            Department.objects
            .annotate(
                steps_count=Count("steps", distinct=True),
                active_managers_count=Count(
                    "employee_memberships",
                    filter=Q(
                        employee_memberships__is_manager=True,
                        employee_memberships__employee__is_active=True,
                    ),
                    distinct=True,
                ),
            )
            .order_by("order")
        )

        task_id = self.request.query_params.get("task_id")

        if task_id not in (None, ""):

            if not str(task_id).isdigit():
                raise ValidationError({"task_id": "مقدار نامعتبر است."})

            queryset = queryset.exclude(tasks__pk=int(task_id))

        return queryset


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