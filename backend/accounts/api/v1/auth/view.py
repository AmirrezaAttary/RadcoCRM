from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from drf_spectacular.utils import extend_schema


from accounts.api.v1.user.serializer import UserAvatarSerializer

from .serializer import (
    LoginSerializer,
    MeSerializer,
    RefreshSerializer,
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
            data=request.data,
            context={"request": request},
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
            request.user,
            context={"request": request},
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


class MeAvatarApi(APIView):
    """
    The logged-in user (admin or employee) manages their own photo.
    """

    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    @extend_schema(
        request=UserAvatarSerializer,
        responses=UserAvatarSerializer,
    )
    def post(self, request):

        serializer = UserAvatarSerializer(
            request.user,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses={204: None})
    def delete(self, request):

        user = request.user

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=["avatar", "updated_at"])

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
