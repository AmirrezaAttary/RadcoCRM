from rest_framework.permissions import BasePermission, IsAuthenticated

from accounts.models.user import User
from access.department import DepartmentAccess
from access.department_step import DepartmentStepAccess
from access.case import CaseAccess
from access.task import TaskAccess
from access.warehouse import WarehouseAccess
from access.internal_task import InternalTaskAccess
from access.purchase import PurchaseAccess
from access.quality_control import QualityControlAccess


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.type == User.UserType.ADMIN
        )


class DepartmentPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        DepartmentAccess.can_access(user=request.user, department=obj)
        return True


class DepartmentStepPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        DepartmentStepAccess.can_access(user=request.user, department_step=obj)
        return True


class CasePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        CaseAccess.can_access(user=request.user, case=obj)
        return True


class TaskPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        TaskAccess.can_access(user=request.user, task=obj)
        return True


class TaskModifyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        TaskAccess.can_modify(user=request.user, task=obj)
        return True


class WarehousePermission(BasePermission):

    def has_permission(self, request, view):
        WarehouseAccess.can_access(user=request.user)
        return True


class InternalTaskPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        InternalTaskAccess.can_access(user=request.user, task=obj)
        return True



class InternalTaskModifyPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        InternalTaskAccess.can_modify(
            user=request.user,
            task=obj,
        )
        return True
    
class PurchasePermission(BasePermission):

    def has_permission(self, request, view):

        PurchaseAccess.can_access(
            user=request.user
        )

        return True


class QualityControlPermission(BasePermission):

    def has_permission(self, request, view):

        QualityControlAccess.can_access(
            user=request.user
        )

        return True
