from django.db import transaction
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import IsAdmin
from hr.models import Contract, ContractSignature

from ..permissions import get_client_ip, is_admin
from .serializer import (
    SignatureDetailSerializer,
    SignatureListSerializer,
    SignatureSignSerializer,
)


class MySignatureListApi(generics.ListAPIView):
    """
    امضاهای مربوط به کارمند لاگین شده.
    ?pending=1 فقط مواردی که هنوز امضا نکرده و قرارداد منتظر امضاست.
    """

    search_fields = ("contract__title",)

    serializer_class = SignatureListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = ContractSignature.objects.filter(
            employee__user=self.request.user,
        ).select_related("employee", "contract", "registered_by")

        if self.request.query_params.get("pending") == "1":
            qs = qs.filter(
                signed_at__isnull=True,
                contract__status=Contract.Status.PENDING,
            )

        return qs


def _do_sign(request, signature_image, *, pk, by_employer):
    with transaction.atomic():

        signature = get_object_or_404(
            ContractSignature.objects.select_related(
                "contract",
                "employee",
            ).select_for_update(of=("self", "contract")),
            pk=pk,
        )

        if not by_employer and signature.employee.user_id != request.user.id:
            raise PermissionDenied("فقط خود کارمند می‌تواند امضا کند.")

        if signature.contract.status != Contract.Status.PENDING:
            raise ValidationError("این قرارداد در وضعیت امضا قرار ندارد.")

        if signature.is_signed:
            raise ValidationError("قبلاً امضا شده است.")

        signature.sign(
            signature_image=signature_image,
            ip=get_client_ip(request),
            registered_by=request.user if by_employer else None,
        )

    return ContractSignature.objects.select_related(
        "employee",
        "contract",
        "registered_by",
    ).get(pk=signature.pk)


class SignatureSignApi(generics.GenericAPIView):
    """
    امضای قرارداد توسط خود کارمند (با حساب کاربری خودش)
    """

    queryset = ContractSignature.objects.all()
    serializer_class = SignatureSignSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=SignatureSignSerializer,
        responses=SignatureListSerializer,
    )
    def post(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signature = _do_sign(
            request,
            serializer.validated_data["signature_image"],
            pk=pk,
            by_employer=False,
        )

        return Response(
            SignatureListSerializer(signature).data,
            status=status.HTTP_200_OK,
        )


class SignatureRegisterApi(generics.GenericAPIView):
    """
    ثبت امضای کارمند توسط کارفرما (ادمین):
    کارفرما امضای کارمند را می‌گیرد (مثلاً روی تبلت) و اینجا ثبت می‌کند.
    """

    queryset = ContractSignature.objects.all()
    serializer_class = SignatureSignSerializer
    permission_classes = (IsAuthenticated, IsAdmin)

    @extend_schema(
        request=SignatureSignSerializer,
        responses=SignatureDetailSerializer,
    )
    def post(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signature = _do_sign(
            request,
            serializer.validated_data["signature_image"],
            pk=pk,
            by_employer=True,
        )

        return Response(
            SignatureDetailSerializer(signature).data,
            status=status.HTTP_200_OK,
        )


class SignatureDetailApi(generics.RetrieveAPIView):
    """
    جزئیات یک امضا (با تصویر)؛ ادمین یا خود امضاکننده
    """

    serializer_class = SignatureDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = ContractSignature.objects.select_related(
            "employee",
            "contract",
            "registered_by",
        )

        if is_admin(self.request.user):
            return qs

        return qs.filter(employee__user=self.request.user)
