from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import (
    generics,
    status,
)
from rest_framework.parsers import (
    JSONParser,
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from absence.models import (
    Absence,
    AbsenceAttachment,
)

from .serializer import (
    AbsenceListSerializer,
    AbsenceRetrieveSerializer,
    AbsenceCreateSerializer,
    AbsenceUpdateSerializer,
    AbsencePatchSerializer,
    AbsenceAttachmentListSerializer,
    AbsenceAttachmentRetrieveSerializer,
    AbsenceAttachmentCreateSerializer,
    AbsenceAttachmentUpdateSerializer,
    AbsenceAttachmentPatchSerializer,
    AbsenceApproveSerializer,
    AbsenceRejectSerializer,
)


class AbsenceListView(
    generics.ListAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AbsenceListSerializer

    def get_queryset(self):
        return (
            Absence.objects
            .select_related(
                "user",
                "user__employee_profile",
                "reviewed_by",
                "reviewed_by__employee_profile",
                "user__profile",
            )
            .filter(
                active=True,
            )
        )


class AbsenceCreateView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AbsenceCreateSerializer

    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )


class AbsenceRetrieveView(
    generics.RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AbsenceRetrieveSerializer

    def get_queryset(self):
        return (
            Absence.objects
            .select_related(
                "user",
                "user__employee_profile",
                "reviewed_by",
                "reviewed_by__employee_profile",
                "user__profile",
            )
            .prefetch_related(
                "attachments",
            )
            .filter(
                active=True,
            )
        )


class AbsenceUpdateView(
    generics.UpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AbsenceUpdateSerializer

    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    http_method_names = [
        "put",
        "options",
        "head",
    ]

    def get_queryset(self):
        return (
            Absence.objects
            .select_related(
                "user",
                "reviewed_by",
            )
            .filter(
                active=True,
            )
        )


class AbsencePatchView(
    generics.UpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AbsencePatchSerializer

    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    http_method_names = [
        "patch",
        "options",
        "head",
    ]

    def get_queryset(self):
        return (
            Absence.objects
            .select_related(
                "user",
                "reviewed_by",
            )
            .filter(
                active=True,
            )
        )


class AbsenceDeleteView(
    generics.DestroyAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return Absence.objects.filter(
            active=True,
        )

    def perform_destroy(self, instance):
        instance.active = False

        instance.save(
            update_fields=[
                "active",
                "updated_at",
            ]
        )


class AbsenceApproveView(
    generics.GenericAPIView
):
    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = AbsenceApproveSerializer

    http_method_names = [
        "post",
        "options",
        "head",
    ]

    @extend_schema(
        request=AbsenceApproveSerializer,
        responses=AbsenceRetrieveSerializer,
    )
    @transaction.atomic
    def post(self, request, pk):

        absence = (
            Absence.objects
            .select_for_update()
            .select_related(
                "user",
                "reviewed_by",
            )
            .filter(
                pk=pk,
                active=True,
            )
            .first()
        )

        if absence is None:
            return Response(
                {
                    "detail": (
                        "مرخصی مورد نظر پیدا نشد."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            absence.status
            != Absence.Status.PENDING
        ):
            return Response(
                {
                    "detail": (
                        "فقط مرخصی‌های در انتظار "
                        "بررسی قابل تأیید هستند."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        absence.status = (
            Absence.Status.APPROVED
        )

        absence.reviewed_by = request.user

        absence.save(
            update_fields=[
                "status",
                "reviewed_by",
                "updated_at",
            ]
        )

        return Response(
            AbsenceRetrieveSerializer(
                absence,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class AbsenceRejectView(
    generics.GenericAPIView
):
    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = AbsenceRejectSerializer

    http_method_names = [
        "post",
        "options",
        "head",
    ]

    @extend_schema(
        request=AbsenceRejectSerializer,
        responses=AbsenceRetrieveSerializer,
    )
    @transaction.atomic
    def post(self, request, pk):

        absence = (
            Absence.objects
            .select_for_update()
            .select_related(
                "user",
                "reviewed_by",
            )
            .filter(
                pk=pk,
                active=True,
            )
            .first()
        )

        if absence is None:
            return Response(
                {
                    "detail": (
                        "مرخصی مورد نظر پیدا نشد."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            absence.status
            != Absence.Status.PENDING
        ):
            return Response(
                {
                    "detail": (
                        "فقط مرخصی‌های در انتظار "
                        "بررسی قابل رد هستند."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        absence.status = (
            Absence.Status.REJECTED
        )

        absence.reviewed_by = request.user

        absence.save(
            update_fields=[
                "status",
                "reviewed_by",
                "updated_at",
            ]
        )

        return Response(
            AbsenceRetrieveSerializer(
                absence,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# AbsenceAttachment
# =========================================================


class AbsenceAttachmentListView(
    generics.ListAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        AbsenceAttachmentListSerializer
    )

    def get_queryset(self):
        return (
            AbsenceAttachment.objects
            .filter(
                absence_id=self.kwargs["absence_id"],
                absence__active=True,
            )
            .select_related(
                "absence",
            )
        )


class AbsenceAttachmentCreateView(
    generics.CreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        AbsenceAttachmentCreateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def perform_create(self, serializer):
        absence = get_object_or_404(
            Absence,
            pk=self.kwargs["absence_id"],
            active=True,
        )

        serializer.save(
            absence=absence,
        )


class AbsenceAttachmentRetrieveView(
    generics.RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        AbsenceAttachmentRetrieveSerializer
    )

    def get_queryset(self):
        return (
            AbsenceAttachment.objects
            .filter(
                absence_id=self.kwargs["absence_id"],
                absence__active=True,
            )
            .select_related(
                "absence",
            )
        )


class AbsenceAttachmentUpdateView(
    generics.UpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        AbsenceAttachmentUpdateSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    http_method_names = [
        "put",
        "options",
        "head",
    ]

    def get_queryset(self):
        return (
            AbsenceAttachment.objects
            .filter(
                absence_id=self.kwargs["absence_id"],
                absence__active=True,
            )
            .select_related(
                "absence",
            )
        )


class AbsenceAttachmentPatchView(
    generics.UpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        AbsenceAttachmentPatchSerializer
    )

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    http_method_names = [
        "patch",
        "options",
        "head",
    ]

    def get_queryset(self):
        return (
            AbsenceAttachment.objects
            .filter(
                absence_id=self.kwargs["absence_id"],
                absence__active=True,
            )
            .select_related(
                "absence",
            )
        )


class AbsenceAttachmentDeleteView(
    generics.DestroyAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return (
            AbsenceAttachment.objects
            .filter(
                absence_id=self.kwargs["absence_id"],
                absence__active=True,
            )
            .select_related(
                "absence",
            )
        )

    def perform_destroy(self, instance):

        if instance.file:
            instance.file.delete(
                save=False,
            )

        instance.delete()