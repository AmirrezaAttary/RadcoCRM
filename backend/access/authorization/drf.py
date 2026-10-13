from rest_framework.permissions import BasePermission

from accounts.models import User, Employee
from .service import AuthorizationService


class HasPermission(BasePermission):
    message = "شما دسترسی لازم برای انجام این عملیات را ندارید."

    def has_permission(self, request, view):
        required_permission = getattr(
            view,
            "required_permission",
            None,
        )

        if not required_permission:
            return True

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.type == User.UserType.ADMIN:
            return True

        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return False

        return AuthorizationService.has_permission(
            employee=employee,
            permission=required_permission,
        )