from rest_framework.exceptions import PermissionDenied


class AccessDenied(PermissionDenied):

    default_detail = "شما سطح دسترسی به این بخش را ندارید."

    default_code = "access_denied"