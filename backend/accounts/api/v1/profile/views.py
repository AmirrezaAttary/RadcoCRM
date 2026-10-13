from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from accounts.models import Profile

from .serializers import ProfileSerializer


class ProfileListView(generics.ListAPIView):

    queryset = Profile.objects.all()

    serializer_class = ProfileSerializer

    permission_classes = (
        IsAuthenticated,
    )


class ProfileDetailView(
    generics.RetrieveAPIView
):

    queryset = Profile.objects.all()

    serializer_class = ProfileSerializer

    permission_classes = (
        IsAuthenticated,
    )


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "full_name": {
                    "type": "string",
                },
                "avatar": {
                    "type": "string",
                    "format": "binary",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                },
                "birth_date": {
                    "type": "string",
                    "format": "date",
                },
            },
        },
    },
)
class ProfileUpdateView(
    generics.UpdateAPIView
):

    serializer_class = ProfileSerializer

    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    http_method_names = [
        "put",
    ]

    def get_queryset(self):
        return Profile.objects.filter(
            user=self.request.user,
        )


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "full_name": {
                    "type": "string",
                },
                "avatar": {
                    "type": "string",
                    "format": "binary",
                },
                "email": {
                    "type": "string",
                    "format": "email",
                },
                "birth_date": {
                    "type": "string",
                    "format": "date",
                },
            },
        },
    },
)
class ProfilePatchView(
    generics.UpdateAPIView
):

    serializer_class = ProfileSerializer

    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    http_method_names = [
        "patch",
    ]

    def get_queryset(self):
        return Profile.objects.filter(
            user=self.request.user,
        )

    def patch(
        self,
        request,
        *args,
        **kwargs,
    ):

        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )