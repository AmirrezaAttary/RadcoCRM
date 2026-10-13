from accounts.models import User, Employee
from department.models import Department, DepartmentEmployee

from access.exceptions import AccessDenied


class DepartmentAccess:

    @classmethod
    def get_queryset(
        cls,
        user,
    ):

        if user.type == User.UserType.ADMIN:
            return Department.objects.all()

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            return Department.objects.none()

        return Department.objects.filter(
            employee_memberships__employee=employee,
        ).distinct()

    @classmethod
    def can_access(
        cls,
        *,
        user,
        department,
    ):

        if user.type == User.UserType.ADMIN:
            return True

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            raise AccessDenied()

        if not DepartmentEmployee.objects.filter(
            employee=employee,
            department=department,
        ).exists():
            raise AccessDenied()

        return True