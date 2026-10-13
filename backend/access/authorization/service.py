from accounts.models import Employee
from access.exceptions import UnknownPermissionError
from access.registry import registry


class AuthorizationService:

    @staticmethod
    def has_permission(*, employee: Employee, permission: str) -> bool:

        if registry.get(permission) is None:
            raise UnknownPermissionError(
                f"Unknown permission: {permission}"
            )

        return Employee.objects.filter(
            pk=employee.pk,
            permission_assignments__permission__code=permission,
            permission_assignments__permission__is_active=True,
            permission_assignments__is_active=True,
        ).exists()