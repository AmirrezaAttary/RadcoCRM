from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from access.permissions import IsAdmin
from accounts.models import User

from .serializer import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserSetPasswordSerializer,
    UserAvatarSerializer,
)


class UserListApi(generics.ListAPIView):
    search_fields = (
        "username",
        "phone_number",
        "employee_profile__full_name",
    )

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


class UserSetPasswordApi(APIView):
    """
    Only admins can change a user's password.
    """

    permission_classes = (IsAdmin,)

    @extend_schema(
        request=UserSetPasswordSerializer,
        responses={200: None},
    )
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        serializer = UserSetPasswordSerializer(
            data=request.data,
            context={"target_user": user, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "رمز عبور با موفقیت تغییر کرد."},
            status=status.HTTP_200_OK,
        )


class UserAvatarApi(APIView):
    """
    Admin sets / removes the photo of any user.
    """

    permission_classes = (IsAdmin,)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=UserAvatarSerializer,
        responses=UserAvatarSerializer,
    )
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        serializer = UserAvatarSerializer(
            user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=["avatar", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)
