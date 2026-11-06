from django.db.models import Count, Q

from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import IsAdmin
from hr.models import Contract

from ..permissions import visible_contracts
from .serializer import (
    ContractCreateSerializer,
    ContractDetailSerializer,
    ContractListSerializer,
    ContractUpdateSerializer,
)


class VisibleContractMixin:
    """
    queryset پایه: فقط قراردادهایی که کاربر اجازه‌ی دیدنشان را دارد
    """

    def get_queryset(self):
        return visible_contracts(
            Contract.objects.select_related("department", "created_by"),
            self.request.user,
        )


class ContractListApi(VisibleContractMixin, generics.ListAPIView):
    """
    فیلتر: ?status=pending  &department=<id>  و جستجو: ?search=متن
    """

    search_fields = ("title", "body", "department__name")

    serializer_class = ContractListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        department = params.get("department")
        if department and department.isdigit():
            qs = qs.filter(department_id=int(department))

        return qs.annotate(
            signatures_count=Count("signatures", distinct=True),
            signed_count=Count(
                "signatures",
                filter=Q(signatures__signed_at__isnull=False),
                distinct=True,
            ),
        )


class ContractCreateApi(generics.CreateAPIView):

    queryset = Contract.objects.all()
    serializer_class = ContractCreateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)


class ContractDetailApi(VisibleContractMixin, generics.RetrieveAPIView):

    serializer_class = ContractDetailSerializer
    permission_classes = (IsAuthenticated,)


class ContractUpdateApi(VisibleContractMixin, generics.UpdateAPIView):

    serializer_class = ContractUpdateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    http_method_names = ("put", "patch", "options")


class ContractDeleteApi(VisibleContractMixin, generics.DestroyAPIView):

    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated, IsAdmin)

    def perform_destroy(self, instance):
        if instance.status not in (
            Contract.Status.DRAFT,
            Contract.Status.CANCELED,
        ):
            raise ValidationError(
                "فقط پیش‌نویس یا قرارداد لغو شده قابل حذف است."
            )
        instance.delete()


class _ActionMixin(VisibleContractMixin):
    """
    ویوهای عملیاتی (ارسال برای امضا / لغو) که بدنه‌ی درخواست ندارند
    """

    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated, IsAdmin)

    def respond(self, request, contract):
        contract = Contract.objects.select_related(
            "department",
            "created_by",
        ).get(pk=contract.pk)

        return Response(
            ContractDetailSerializer(
                contract,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )


class ContractSendApi(_ActionMixin, generics.GenericAPIView):

    @extend_schema(request=None, responses=ContractDetailSerializer)
    def post(self, request, pk):
        contract = self.get_object()

        if not contract.is_draft:
            raise ValidationError("این قرارداد قبلاً ارسال شده است.")

        if not contract.get_signing_employees().exists():
            raise ValidationError(
                "در این دپارتمان کارمند فعالی برای امضا وجود ندارد."
            )

        contract.send_for_signature()

        return self.respond(request, contract)


class ContractCancelApi(_ActionMixin, generics.GenericAPIView):

    @extend_schema(request=None, responses=ContractDetailSerializer)
    def post(self, request, pk):
        contract = self.get_object()

        if contract.status not in (
            Contract.Status.DRAFT,
            Contract.Status.PENDING,
        ):
            raise ValidationError("این قرارداد قابل لغو نیست.")

        contract.cancel()

        return self.respond(request, contract)
