from tasks.models.tasks import Task
from accounts.models import User
from .exceptions import AccessDenied


class TaskAccess:

    @staticmethod
    def get_queryset(user: User):

        if not user.is_authenticated:
            return Task.objects.none()

        # Admin
        if user.type == User.UserType.ADMIN:
            return (
                Task.objects
                .select_related(
                    "case",
                    "department",
                    "current_step",
                    "created_by",
                )
                .prefetch_related(
                    "assigned_employee",
                )
            )

        try:
            employee = user.employee_profile
        except Exception:
            return Task.objects.none()

        return (
            Task.objects.filter(
                assigned_employee=employee
            )
            | Task.objects.filter(
                created_by=user
            )
        ).distinct().select_related(
            "case",
            "department",
            "current_step",
            "created_by",
        ).prefetch_related(
            "assigned_employee",
        )

    @staticmethod
    def can_access(user: User, task: Task):

        # Admin
        if user.type == User.UserType.ADMIN:
            return

        # Creator
        if task.created_by == user:
            return

        try:
            employee = user.employee_profile
        except Exception:
            raise AccessDenied

        # Assigned employee
        if not task.assigned_employee.filter(
            pk=employee.pk,
        ).exists():
            raise AccessDenied

    @staticmethod
    def can_modify(user: User, task: Task):

        # Admin
        if user.type == User.UserType.ADMIN:
            return

        # Creator
        if task.created_by == user:
            return

        try:
            employee = user.employee_profile
        except Exception:
            raise AccessDenied

        # Assigned employee
        if not task.assigned_employee.filter(
            pk=employee.pk
        ).exists():
            raise AccessDenied