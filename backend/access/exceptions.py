from rest_framework.exceptions import PermissionDenied

class AccessDenied(Exception):
    pass


class UnknownPermissionError(Exception):
    pass