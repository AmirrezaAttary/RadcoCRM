from accounts.models import User, Employee
from access.exceptions import AccessDenied
from warehouse.models.warehouse_staff import WarehouseStaff


class WarehouseAccess:

    @classmethod
    def get_queryset(cls, user, model):
        if user.type == User.UserType.ADMIN:
            return model.objects.all()

        try:
            employee = user.employee_profileemployee.warehouse_staff
        except (Employee.DoesNotExist, WarehouseStaff.DoesNotExist):
            return model.objects.none()

        return model.objects.all()

    @classmethod
    def can_access(cls, *, user):
        if user.type == User.UserType.ADMIN:
            return True

        try:
            employee = user.employee_profile
            employee.warehouse_staff
        except (Employee.DoesNotExist, WarehouseStaff.DoesNotExist):
            raise AccessDenied()

        return True
