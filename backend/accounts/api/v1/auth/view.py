from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from drf_spectacular.utils import extend_schema


from .serializer import (
    LoginSerializer,
    MeSerializer,
    RefreshSerializer,
    ChangePasswordSerializer,
)


@extend_schema(
    request=LoginSerializer,
    responses=LoginSerializer,
)
class LoginApi(APIView):

    authentication_classes = ()
    permission_classes = ()

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )

class MeApi(APIView):

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):

        serializer = MeSerializer(
            request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

class RefreshTokenApi(APIView):

    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=RefreshSerializer,
        responses=RefreshSerializer,
    )

    def post(self, request):

        serializer = RefreshSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )
        
class ChangePasswordApi(APIView):

    permission_classes = (
        IsAdminUser,
    )

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: None,
        },
    )
    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": "رمز عبور کاربر با موفقیت تغییر کرد."
            },
            status=status.HTTP_200_OK,
        )