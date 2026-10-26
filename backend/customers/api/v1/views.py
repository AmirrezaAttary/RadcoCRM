from django.db.models import Exists, OuterRef, Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from access.case import CaseAccess
from accounts.models import User
from customers.models import Customer, CustomerScore
from .serializers import (
    CustomerListSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerDetailSerializer,
    CustomerScoreSerializer,
)
from . paginations import CustomerPagination

class CustomerListApi(generics.ListAPIView):
    """
    لیست مشتریان؛ تمام فیلترها سمت سرور اعمال می‌شوند.

    ?page=2 & ?page_size=20   → صفحه‌بندی
    ?status=1|2               → بالقوه / بالفعل
    ?search=...               → جستجو (نام، موبایل، شرکت، سمت)
    ?scope=mine               → فقط مشتریان مربوط به کاربر جاری
                                (ثبت‌کننده یا دارای پرونده‌ای که کاربر به آن دسترسی دارد).
                                برای ادمین همیشه همهٔ مشتریان برمی‌گردد.

    هر آیتم فیلد has_case دارد (آیا پرونده‌ای قابل‌دسترس برای کاربر دارد)؛
    پس فرانت‌اند دیگر لازم نیست همهٔ پرونده‌ها را جدا بخواند.
    """

    search_fields = (
        "full_name",
        "phone_number",
        "company_name",
        "job_title",
    )

    serializer_class = CustomerListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params

        visible_cases = CaseAccess.get_queryset(user).order_by()

        queryset = (
            Customer.objects
            .select_related("created_by")
            .annotate(
                has_case=Exists(
                    visible_cases.filter(customer=OuterRef("pk"))
                ),
            )
        )

        if (
            params.get("scope") == "mine"
            and user.type != User.UserType.ADMIN
        ):
            queryset = queryset.filter(
                Q(created_by=user) | Q(has_case=True)
            )

        status_param = params.get("status")
        valid_statuses = {
            str(value) for value in Customer.CustomerStatus.values
        }
        if status_param in valid_statuses:
            queryset = queryset.filter(status=int(status_param))

        return queryset.order_by("-created_at", "-id")


class CustomerCreateApi(generics.CreateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerCreateSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )


class CustomerDetailApi(generics.RetrieveAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CustomerUpdateApi(generics.UpdateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerUpdateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CustomerDeleteApi(generics.DestroyAPIView):

    queryset = Customer.objects.all()

    permission_classes = (
        IsAuthenticated,
    )


class CustomerScoreListCreateView(generics.ListCreateAPIView):
    search_fields = (
        "reason",
        "created_by__full_name",
    )

    serializer_class = CustomerScoreSerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]

        return CustomerScore.objects.filter(
            customer_id=customer_id
        ).select_related(
            "customer",
            "created_by",
        )

    def perform_create(self, serializer):
        customer_id = self.kwargs["customer_id"]

        serializer.save(
            customer_id=customer_id
        )


class CustomerScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerScoreSerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]

        return CustomerScore.objects.filter(
            customer_id=customer_id
        ).select_related(
            "customer",
            "created_by",
        )

    def perform_update(self, serializer):
        customer_id = self.kwargs["customer_id"]

        if serializer.validated_data.get("customer"):
            if serializer.validated_data["customer"].id != int(customer_id):
                raise ValidationError({
                    "customer_id": "شناسه مشتری با مشتری موجود در URL مطابقت ندارد."
                })

        serializer.save()