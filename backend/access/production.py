from accounts.models import User
from access.exceptions import AccessDenied


class ProductionAccess:

    @classmethod
    def can_access(cls, *, user):
        # کاربر ناشناس
        if not user or not user.is_authenticated:
            raise AccessDenied()

        # فعلاً فقط مدیر به بخش تولید دسترسی دارد
        if user.type == User.UserType.ADMIN:
            return True

        raise AccessDenied()
