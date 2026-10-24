from django.db.models import ProtectedError

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from access.case import CaseAccess
from access.permissions import CasePermission

from tasks.models import Case, Resource

from .serializers import (
    CaseListSerializer,
    CaseCreateSerializer,
    CaseUpdateSerializer,
    CaseDetailSerializer,
    CaseActivateSerializer,
    CaseDeactivateSerializer,
    ResourceListSerializer,
    ResourceCreateSerializer,
    ResourceUpdateSerializer,
    ResourceDetailSerializer,
)

from tasks.services.tasks import (
    activate_case,
    deactivate_case,
)




class CaseListApi(generics.ListAPIView):

    search_fields = (
        "title",
        "description",
        "customer__full_name",
    )

    serializer_class = CaseListSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return CaseAccess.get_queryset(
            self.request.user,
        )


class CaseCreateApi(generics.CreateAPIView):

    queryset = Case.objects.all()

    serializer_class = CaseCreateSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def perform_create(self, serializer):
        customer = serializer.validated_data["customer"]



        serializer.save(
            created_by=self.request.user,
        )


class CaseDetailApi(generics.RetrieveAPIView):

    queryset = Case.objects.all()

    serializer_class = CaseDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CaseUpdateApi(generics.UpdateAPIView):

    queryset = Case.objects.all()

    serializer_class = CaseUpdateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CaseDeleteApi(generics.DestroyAPIView):

    queryset = Case.objects.all()

    permission_classes = (
        IsAuthenticated,
    )

    def perform_destroy(self, instance):
        try:
            instance.delete()

        except ProtectedError:
            raise ValidationError(
                "این پرونده دارای تسک است و قابل حذف نیست."
            )


class ResourceListApi(generics.ListAPIView):

    search_fields = (
        "title",
    )

    queryset = Resource.objects.all()

    serializer_class = ResourceListSerializer

    permission_classes = (
        IsAuthenticated,
    )


class ResourceCreateApi(generics.CreateAPIView):

    queryset = Resource.objects.all()

    serializer_class = ResourceCreateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class ResourceDetailApi(generics.RetrieveAPIView):

    queryset = Resource.objects.all()

    serializer_class = ResourceDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )


class ResourceUpdateApi(generics.UpdateAPIView):

    queryset = Resource.objects.all()

    serializer_class = ResourceUpdateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class ResourceDeleteApi(generics.DestroyAPIView):

    queryset = Resource.objects.all()

    permission_classes = (
        IsAuthenticated,
    )

    def perform_destroy(self, instance):

        if instance.cases.exists():

            raise ValidationError(
                "این منبع در پرونده‌ها استفاده شده است و قابل حذف نیست."
            )

        instance.delete()
        
class CaseActivateApi(generics.GenericAPIView):

    queryset = Case.objects.all()

    serializer_class = CaseActivateSerializer

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):
        case = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        case = activate_case(
            case=case,
        )

        return Response(
            CaseDetailSerializer(
                case,
            ).data
        )


class CaseDeactivateApi(generics.GenericAPIView):

    queryset = Case.objects.all()

    serializer_class = CaseDeactivateSerializer

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, pk):
        case = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        case = deactivate_case(
            case=case,
        )

        return Response(
            CaseDetailSerializer(
                case,
            ).data
        )