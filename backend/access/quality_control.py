from accounts.models import User
from access.exceptions import AccessDenied
from quality_control.models.employee import QualityControlEmployee


class QualityControlAccess:

    @classmethod
    def can_access(cls, *, user):

        if user.type == User.UserType.ADMIN:
            return True

        try:
            quality_control_employee = (
                user.quality_control_employee
            )
        except QualityControlEmployee.DoesNotExist:
            raise AccessDenied()

        if not quality_control_employee.is_active:
            raise AccessDenied()

        return True