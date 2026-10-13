from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from access.authorization.drf import HasPermission

from .serializer import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


class UserListApi(generics.ListAPIView):

    queryset = User.objects.all()

    serializer_class = UserListSerializer

    permission_classes = (
        IsAuthenticated,
    )


class UserCreateApi(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = UserCreateSerializer

    required_permission = "users.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class UserDetailApi(generics.RetrieveAPIView):

    queryset = User.objects.all()

    serializer_class = UserListSerializer

    permission_classes = (
        IsAuthenticated,
    )


class UserUpdateApi(generics.UpdateAPIView):

    queryset = User.objects.all()

    serializer_class = UserUpdateSerializer

    required_permission = "users.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )


class UserDeleteApi(generics.DestroyAPIView):

    queryset = User.objects.all()

    required_permission = "users.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )