from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentication import (
    IsPortalAccount,
    PortalJWTAuthentication,
    PortalLoginThrottle,
    PortalAccessToken,
    issue_token,
    verify_credentials,
)
from ...models import CustomerOrder, CustomerPortalAccount
from ...permissions import IsAdminOrWarehouseStaff, IsPortalAdmin
from ...services import (
    PortalConfigError,
    dispatch_to_warehouses,
    generate_password,
    products_with_stock,
)
from .serializers import (
    AccountCreateSerializer,
    AccountListSerializer,
    AccountPasswordSerializer,
    AccountUpdateSerializer,
    OrderApproveSerializer,
    OrderCreateSerializer,
    OrderRejectSerializer,
    OrderSerializer,
    StaffOrderSerializer,
    PortalLoginSerializer,
    PortalMeSerializer,
    PortalProductSerializer,
)


def _orders_queryset():
    return (
        CustomerOrder.objects
        .select_related("customer")
        .prefetch_related("items__product")
    )


def _staff_orders_queryset():
    return (
        _orders_queryset()
        .select_related("task")
        .prefetch_related("task__order_tasks__warehouse")
    )


# ═════════════ ۱) مدیریت حساب مشتریان — فقط ادمین ═════════════

class AccountListApi(generics.ListAPIView):
    """?is_active=true|false  ،  ?search=نام/موبایل/شرکت/نام‌کاربری"""

    search_fields = (
        "username",
        "customer__full_name",
        "customer__phone_number",
        "customer__company_name",
    )
    serializer_class = AccountListSerializer
    permission_classes = (IsPortalAdmin,)

    def get_queryset(self):
        queryset = (
            CustomerPortalAccount.objects
            .select_related("customer", "granted_by")
            .order_by("-created_at")
        )

        is_active = self.request.query_params.get("is_active")
        if is_active in ("true", "1"):
            queryset = queryset.filter(is_active=True)
        elif is_active in ("false", "0"):
            queryset = queryset.filter(is_active=False)

        return queryset


class AccountCreateApi(generics.CreateAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = (IsPortalAdmin,)


class AccountDetailApi(generics.RetrieveAPIView):
    queryset = CustomerPortalAccount.objects.select_related("customer", "granted_by")
    serializer_class = AccountListSerializer
    permission_classes = (IsPortalAdmin,)


class AccountUpdateApi(generics.UpdateAPIView):
    queryset = CustomerPortalAccount.objects.all()
    serializer_class = AccountUpdateSerializer
    permission_classes = (IsPortalAdmin,)


class AccountDeleteApi(generics.DestroyAPIView):
    queryset = CustomerPortalAccount.objects.all()
    permission_classes = (IsPortalAdmin,)


class AccountSetPasswordApi(APIView):
    """تغییر رمز توسط ادمین؛ بدون password، رمز تصادفی ساخته می‌شود."""

    permission_classes = (IsPortalAdmin,)

    @extend_schema(request=AccountPasswordSerializer, responses={200: None})
    def post(self, request, pk):
        account = get_object_or_404(CustomerPortalAccount, pk=pk)

        serializer = AccountPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_password = serializer.validated_data.get("password")
        generated = not raw_password

        if generated:
            raw_password = generate_password()

        account.set_password(raw_password)
        account.save(update_fields=["password", "updated_at"])

        data = {"detail": "رمز عبور تغییر کرد."}
        if generated:
            data["generated_password"] = raw_password

        return Response(data)


# ═════════════ ۲) بررسی سفارش‌ها — ادمین / کارمند انبار ═════════════
# مرحله ۱: کارمند تأیید/رد می‌کند (اینجا). مرحله ۲: انباردار روی تسک انبار
# با endpoint موجود order_task/<id>/confirm/ تأیید می‌کند.

class StaffOrderListApi(generics.ListAPIView):
    """?status=pending|in_warehouse|confirmed|partial|rejected  ،  ?customer=<id>"""

    search_fields = (
        "customer__full_name",
        "customer__company_name",
        "customer__phone_number",
        "account__username",
    )
    serializer_class = StaffOrderSerializer
    permission_classes = (IsAdminOrWarehouseStaff,)

    def get_queryset(self):
        queryset = _staff_orders_queryset()
        params = self.request.query_params

        status_value = params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        customer = params.get("customer")
        if customer and customer.isdigit():
            queryset = queryset.filter(customer_id=int(customer))

        return queryset


class StaffOrderDetailApi(generics.RetrieveAPIView):
    queryset = _staff_orders_queryset()
    serializer_class = StaffOrderSerializer
    permission_classes = (IsAdminOrWarehouseStaff,)


class StaffOrderApproveApi(APIView):
    """
    تأیید سفارش توسط کارمند؛ همین‌جا تسک انبار برای هر انبار ساخته می‌شود.
    اگر موجودی کافی نباشد، تأیید انجام نمی‌شود و سفارش pending می‌ماند.
    """

    permission_classes = (IsAdminOrWarehouseStaff,)

    @extend_schema(request=OrderApproveSerializer, responses=StaffOrderSerializer)
    def post(self, request, pk):
        serializer = OrderApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = get_object_or_404(
                CustomerOrder.objects.select_for_update(), pk=pk
            )

            if order.status != CustomerOrder.Status.PENDING:
                raise ValidationError("فقط سفارش در انتظار تأیید کارمند قابل تأیید است.")

            order.staff_note = serializer.validated_data["staff_note"]
            order.handled_by = request.user
            order.save(update_fields=["staff_note", "handled_by", "updated_at"])

            try:
                dispatch_to_warehouses(order, creator=request.user)
            except ValueError as exc:
                raise ValidationError(str(exc))
            except PortalConfigError as exc:
                raise ValidationError(str(exc))

        order = get_object_or_404(_staff_orders_queryset(), pk=pk)
        return Response(StaffOrderSerializer(order).data)


class StaffOrderRejectApi(APIView):
    """رد سفارش توسط کارمند (دلیل الزامی است)."""

    permission_classes = (IsAdminOrWarehouseStaff,)

    @extend_schema(request=OrderRejectSerializer, responses=StaffOrderSerializer)
    def post(self, request, pk):
        serializer = OrderRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = get_object_or_404(
                CustomerOrder.objects.select_for_update(), pk=pk
            )

            if order.status != CustomerOrder.Status.PENDING:
                raise ValidationError("فقط سفارش در انتظار تأیید کارمند قابل رد است.")

            order.status = CustomerOrder.Status.REJECTED
            order.staff_note = serializer.validated_data["staff_note"]
            order.handled_by = request.user
            order.save(update_fields=["status", "staff_note", "handled_by", "updated_at"])

        order = get_object_or_404(_staff_orders_queryset(), pk=pk)
        return Response(StaffOrderSerializer(order).data)


# ═════════════ ۳) پرتال مشتری ═════════════

class PortalAuthMixin:
    authentication_classes = (PortalJWTAuthentication,)
    permission_classes = (IsPortalAccount,)


class PortalLoginApi(APIView):

    authentication_classes = ()
    permission_classes = ()
    throttle_classes = (PortalLoginThrottle,)

    @extend_schema(request=PortalLoginSerializer, responses={200: None})
    def post(self, request):
        serializer = PortalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = verify_credentials(
            serializer.validated_data["username"].strip(),
            serializer.validated_data["password"],
        )

        if account is None:
            return Response(
                {"detail": "نام کاربری یا رمز عبور اشتباه است."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        account.last_login = timezone.now()
        account.save(update_fields=["last_login"])

        return Response({
            "access": str(issue_token(account)),
            "expires_in": int(PortalAccessToken.lifetime.total_seconds()),
            "account": PortalMeSerializer(account).data,
        })


class PortalMeApi(PortalAuthMixin, generics.RetrieveAPIView):
    serializer_class = PortalMeSerializer

    def get_object(self):
        return self.request.user


class PortalProductListApi(PortalAuthMixin, generics.ListAPIView):
    """کالاهای دارای موجودی. ?search=...  ،  ?category=<id>"""

    search_fields = ("name",)
    serializer_class = PortalProductSerializer

    def get_queryset(self):
        queryset = (
            products_with_stock()
            .select_related(
                "category",
                "dimension_unit",
                "weight_unit",
                "volume_unit",
                "area_unit",
                "count_unit",
            )
            .order_by("name")
        )

        category = self.request.query_params.get("category")
        if category and category.isdigit():
            queryset = queryset.filter(category_id=int(category))

        return queryset


class PortalOrderListCreateApi(PortalAuthMixin, generics.ListCreateAPIView):

    def get_queryset(self):
        return _orders_queryset().filter(customer=self.request.user.customer)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    @extend_schema(request=OrderCreateSerializer, responses=OrderSerializer)
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class PortalOrderDetailApi(PortalAuthMixin, generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return _orders_queryset().filter(customer=self.request.user.customer)
