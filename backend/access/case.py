from django.db.models import Q

from accounts.models import User, Employee
from tasks.models import Case

from access.exceptions import AccessDenied


class CaseAccess:

    @classmethod
    def get_queryset(
        cls,
        user,
    ):

        if user.type == User.UserType.ADMIN:
            return Case.objects.all()

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            return Case.objects.filter(
                created_by=user,
            )

        return Case.objects.filter(
            Q(created_by=user)
            | Q(tasks__assigned_employee=employee)
        ).distinct()

    @classmethod
    def can_access(
        cls,
        *,
        user,
        case,
    ):

        if user.type == User.UserType.ADMIN:
            return True

        if case.created_by_id == user.id:
            return True

        try:
            employee = user.employee_profile

        except Employee.DoesNotExist:
            raise AccessDenied()

        if not case.tasks.filter(
            assigned_employee=employee,
        ).exists():
            raise AccessDenied()

        return True