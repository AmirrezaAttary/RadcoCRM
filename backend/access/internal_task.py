from tasks.models.internal_task import InternalTask
from accounts.models import User
from .exceptions import AccessDenied


class InternalTaskAccess:

    @staticmethod
    def get_queryset(user: User):

        # =====================================================
        # Admin
        # =====================================================

        if user.type == User.UserType.ADMIN:

            return (
                InternalTask.objects
                .select_related(
                    "deadline",
                    "created_by",
                )
                .prefetch_related(
                    "assigned_to",
                )
            )

        # =====================================================
        # Employee
        #
        # assigned_to now points directly to User
        # =====================================================

        return (
            InternalTask.objects.filter(
                assigned_to=user
            )
            | InternalTask.objects.filter(
                created_by=user
            )
        ).distinct().select_related(
            "deadline",
            "created_by",
        ).prefetch_related(
            "assigned_to",
        )

    @staticmethod
    def can_access(
        user: User,
        task: InternalTask,
    ):

        # =====================================================
        # Admin
        # =====================================================

        if user.type == User.UserType.ADMIN:
            return

        # =====================================================
        # Creator
        # =====================================================

        if task.created_by == user:
            return

        # =====================================================
        # Assigned User
        #
        # assigned_to is now ManyToMany -> User
        # =====================================================

        if task.assigned_to.filter(
            pk=user.pk
        ).exists():
            return

        raise AccessDenied

    @staticmethod
    def can_modify(
        user: User,
        task: InternalTask,
    ):

        # =====================================================
        # Admin
        # =====================================================

        if user.type == User.UserType.ADMIN:
            return

        # =====================================================
        # Creator
        # =====================================================

        if task.created_by == user:
            return

        # =====================================================
        # Assigned User
        # =====================================================

        if task.assigned_to.filter(
            pk=user.pk
        ).exists():
            return

        raise AccessDenied