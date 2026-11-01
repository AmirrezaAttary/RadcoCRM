from django.urls import path

from .views import (
    AccountCreateApi,
    AccountDeleteApi,
    AccountDetailApi,
    AccountListApi,
    AccountSetPasswordApi,
    AccountUpdateApi,
    PortalLoginApi,
    PortalMeApi,
    PortalOrderDetailApi,
    PortalOrderListCreateApi,
    PortalProductListApi,
    StaffOrderDetailApi,
    StaffOrderApproveApi,
    StaffOrderListApi,
    StaffOrderRejectApi,
)

urlpatterns = [
    # ── ادمین: مدیریت حساب مشتریان ──
    path("accounts/list/", AccountListApi.as_view(), name="portal-account-list"),
    path("accounts/create/", AccountCreateApi.as_view(), name="portal-account-create"),
    path("accounts/<int:pk>/", AccountDetailApi.as_view(), name="portal-account-detail"),
    path("accounts/<int:pk>/update/", AccountUpdateApi.as_view(), name="portal-account-update"),
    path("accounts/<int:pk>/set-password/", AccountSetPasswordApi.as_view(), name="portal-account-set-password"),
    path("accounts/<int:pk>/delete/", AccountDeleteApi.as_view(), name="portal-account-delete"),

    # ── ادمین / کارمند انبار: بررسی (تأیید/رد) سفارش‌های مشتریان ──
    path("orders/list/", StaffOrderListApi.as_view(), name="portal-staff-order-list"),
    path("orders/<int:pk>/", StaffOrderDetailApi.as_view(), name="portal-staff-order-detail"),
    path("orders/<int:pk>/approve/", StaffOrderApproveApi.as_view(), name="portal-staff-order-approve"),
    path("orders/<int:pk>/reject/", StaffOrderRejectApi.as_view(), name="portal-staff-order-reject"),

    # ── مشتری ──
    path("portal/login/", PortalLoginApi.as_view(), name="portal-login"),
    path("portal/me/", PortalMeApi.as_view(), name="portal-me"),
    path("portal/products/", PortalProductListApi.as_view(), name="portal-products"),
    path("portal/orders/", PortalOrderListCreateApi.as_view(), name="portal-orders"),
    path("portal/orders/<int:pk>/", PortalOrderDetailApi.as_view(), name="portal-order-detail"),
]
