
from accounts.models import User, Employee
from access.exceptions import AccessDenied
from warehouse.models.warehouse_staff import WarehouseStaff


class WarehouseAccess:

    @classmethod
    def get_queryset(cls, user, model):
        # جلوگیری از دسترسی کاربران ناشناس
        if not user or not user.is_authenticated:
            return model.objects.none()

        # مدیر به تمام رکوردها دسترسی دارد
        if user.type == User.UserType.ADMIN:
            return model.objects.all()

        try:
            employee = user.employee_profile
            warehouse_staff = employee.warehouse_staff
        except (
            Employee.DoesNotExist,
            WarehouseStaff.DoesNotExist,
            AttributeError,
        ):
            return model.objects.none()

        # مطابق منطق قبلی، کارمند انبار فقط پس از احراز
        # ارتباط با پروفایل انبارداری به این بخش می‌رسد.
        return model.objects.all()

    @classmethod
    def can_access(cls, *, user):
        # کاربر ناشناس نباید به ویژگی type دسترسی داده شود
        if not user or not user.is_authenticated:
            raise AccessDenied()

        # مدیر مجاز است
        if user.type == User.UserType.ADMIN:
            return True

        # سایر کاربران باید پروفایل کارمند و انباردار داشته باشند
        try:
            employee = user.employee_profile
            employee.warehouse_staff
        except (
            Employee.DoesNotExist,
            WarehouseStaff.DoesNotExist,
            AttributeError,
        ):
            raise AccessDenied()

        return True
