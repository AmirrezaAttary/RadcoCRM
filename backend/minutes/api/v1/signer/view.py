from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from minutes.models import Meeting, Signer

from ..permissions import IsMeetingOwnerOrAdmin, get_client_ip
from .serializer import (
    PublicSignerSerializer,
    SignerCreateSerializer,
    SignerListSerializer,
    SignerSignSerializer,
    SignerUpdateSerializer,
)


class MySignerListApi(generics.ListAPIView):
    """
    امضاهای مربوط به کاربر لاگین شده.
    ?pending=1 فقط مواردی که هنوز امضا نکرده و صورت جلسه منتظر امضاست.
    """

    search_fields = (
        "full_name",
        "phone_number",
        "role_title",
        "meeting__title",
    )


    serializer_class = SignerListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Signer.objects.filter(
            user=self.request.user,
        ).select_related("user__employee_profile", "meeting")

        if self.request.query_params.get("pending") == "1":
            qs = qs.filter(
                signed_at__isnull=True,
                meeting__status=Meeting.Status.PENDING,
            )

        return qs


class SignerCreateApi(generics.CreateAPIView):

    queryset = Signer.objects.all()
    serializer_class = SignerCreateSerializer
    permission_classes = (IsAuthenticated,)


class SignerUpdateApi(generics.UpdateAPIView):

    queryset = Signer.objects.select_related("meeting")
    serializer_class = SignerUpdateSerializer
    permission_classes = (IsAuthenticated, IsMeetingOwnerOrAdmin)
    http_method_names = ("put", "patch", "options")


class SignerDeleteApi(generics.DestroyAPIView):

    queryset = Signer.objects.select_related("meeting")
    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated, IsMeetingOwnerOrAdmin)

    def perform_destroy(self, instance):
        if not instance.meeting.is_draft:
            raise ValidationError(
                "فقط از صورت جلسه‌ی پیش‌نویس می‌شود امضاکننده حذف کرد."
            )
        instance.delete()


def _do_sign(request, signature_image, *, pk=None, token=None):
    """
    منطق مشترک امضا برای امضای کاربر سیستم (با pk) و شخص بیرونی (با token)
    """
    lookup = {"pk": pk} if pk is not None else {"token": token}

    with transaction.atomic():

        signer = get_object_or_404(
            Signer.objects.select_related("meeting").select_for_update(
                of=("self", "meeting"),
            ),
            **lookup,
        )

        if pk is not None:
            # حتی ادمین هم نمی‌تواند به جای دیگران امضا کند
            if signer.user_id != request.user.id:
                raise PermissionDenied("فقط خود امضاکننده می‌تواند امضا کند.")
        elif not signer.is_external:
            raise PermissionDenied(
                "این امضاکننده باید با حساب کاربری خودش امضا کند."
            )

        if signer.meeting.status != Meeting.Status.PENDING:
            raise ValidationError("این صورت جلسه در وضعیت امضا قرار ندارد.")

        if signer.is_signed:
            raise ValidationError("قبلاً امضا شده است.")

        signer.sign(
            signature_image=signature_image,
            ip=get_client_ip(request),
        )

    return Signer.objects.select_related("user__employee_profile").get(
        pk=signer.pk
    )


class SignerSignApi(generics.GenericAPIView):
    """
    امضای صورت جلسه توسط خود امضاکننده (کاربر سیستم)
    """

    queryset = Signer.objects.all()
    serializer_class = SignerSignSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=SignerSignSerializer,
        responses=SignerListSerializer,
    )
    def post(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signer = _do_sign(
            request,
            serializer.validated_data["signature_image"],
            pk=pk,
        )

        return Response(
            SignerListSerializer(signer).data,
            status=status.HTTP_200_OK,
        )


class PublicSignerDetailApi(generics.GenericAPIView):
    """
    دیدن صورت جلسه با لینک امضا (بدون لاگین، فقط افراد بیرونی)
    """

    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicSignerSerializer
    queryset = Signer.objects.all()

    @extend_schema(responses=PublicSignerSerializer)
    def get(self, request, token):
        signer = get_object_or_404(
            Signer.objects.select_related("meeting", "user__employee_profile"),
            token=token,
            user__isnull=True,
        )

        if signer.meeting.status == Meeting.Status.DRAFT:
            raise Http404

        return Response(PublicSignerSerializer(signer).data)


class PublicSignerSignApi(generics.GenericAPIView):
    """
    امضای شخص بیرونی با لینک (بدون لاگین)
    """

    authentication_classes = ()
    permission_classes = ()
    serializer_class = SignerSignSerializer
    queryset = Signer.objects.all()

    @extend_schema(
        request=SignerSignSerializer,
        responses=PublicSignerSerializer,
    )
    def post(self, request, token):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signer = _do_sign(
            request,
            serializer.validated_data["signature_image"],
            token=token,
        )

        return Response(PublicSignerSerializer(signer).data)
