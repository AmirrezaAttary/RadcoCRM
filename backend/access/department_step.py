from accounts.models import User, Employee
from department.models import DepartmentEmployee
from department.models.department_step import DepartmentStep

from access.exceptions import AccessDenied


class DepartmentStepAccess:

    @classmethod
    def get_queryset(
        cls,
        user,
    ):

        if user.type == User.UserType.ADMIN:
            return DepartmentStep.objects.all()

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            return DepartmentStep.objects.none()

        return DepartmentStep.objects.filter(
            department__employee_memberships__employee=employee,
        ).distinct()

    @classmethod
    def can_access(
        cls,
        *,
        user,
        department_step,
    ):

        if user.type == User.UserType.ADMIN:
            return True

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            raise AccessDenied()

        if not DepartmentEmployee.objects.filter(
            employee=employee,
            department=department_step.department,
        ).exists():
            raise AccessDenied()

        return True