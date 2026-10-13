from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from accounts.models import User

from .serializer import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


class UserListApi(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class UserCreateApi(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (IsAdminUser,)


class UserDetailApi(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAdminUser,)


class UserUpdateApi(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAdminUser,)


class UserDeleteApi(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)