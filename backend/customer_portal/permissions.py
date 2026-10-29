from rest_framework.permissions import BasePermission

from accounts.models import Employee, User
from warehouse.models.warehouse_staff import WarehouseStaff


class IsPortalAdmin(BasePermission):
    """فقط ادمین: ساخت/ویرایش حساب پرتال مشتریان."""

    message = "فقط ادمین می‌تواند این عملیات را انجام دهد."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.type == User.UserType.ADMIN or user.is_superuser)
        )


class IsAdminOrWarehouseStaff(BasePermission):
    """ادمین یا کارمند انبار: بررسی سفارش‌های مشتریان."""

    message = "شما به سفارش‌های مشتریان دسترسی ندارید."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.type == User.UserType.ADMIN or user.is_superuser:
            return True

        try:
            staff = user.employee_profile.warehouse_staff
        except (Employee.DoesNotExist, WarehouseStaff.DoesNotExist, AttributeError):
            return False

        return staff.is_active
