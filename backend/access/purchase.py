from accounts.models import User, Employee
from access.exceptions import AccessDenied
from purchasing.models.purchase_employee import PurchaseProcessEmployee


class PurchaseAccess:

    @classmethod
    def can_access(cls, *, user):

        if user.type == User.UserType.ADMIN:
            return True

        try:
            employee = user.employee_profile

            purchase_employee = (
                employee.purchase_process_employee
            )

        except (
            Employee.DoesNotExist,
            PurchaseProcessEmployee.DoesNotExist,
        ):
            raise AccessDenied()

        if not purchase_employee.is_active:
            raise AccessDenied()

        return True