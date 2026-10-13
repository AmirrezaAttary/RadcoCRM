from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from accounts.models import User
from access.models import Permission
from access.api.v1.serializers.permission import PermissionListSerializer


class PermissionListApi(generics.ListAPIView):

    serializer_class = PermissionListSerializer
    permission_classes = [
        IsAdminUser,
    ]

    def get_queryset(self):
        if self.request.user.type != User.UserType.ADMIN:
            return Permission.objects.none()

        return Permission.objects.filter(
            is_active=True,
        ).order_by(
            "resource",
            "action",
        )