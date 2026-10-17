from django.db.models import Count, Q

from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from minutes.models import Meeting

from ..permissions import IsMeetingOwnerOrAdmin, visible_meetings
from .serializer import (
    MeetingCreateSerializer,
    MeetingDetailSerializer,
    MeetingListSerializer,
    MeetingUpdateSerializer,
)


class VisibleMeetingMixin:
    """
    queryset پایه: فقط صورت‌جلسه‌هایی که کاربر اجازه‌ی دیدنشان را دارد
    """

    def get_queryset(self):
        return visible_meetings(
            Meeting.objects.select_related("created_by"),
            self.request.user,
        )


class MeetingListApi(VisibleMeetingMixin, generics.ListAPIView):
    """
    فیلتر: ?status=pending  و جستجو: ?search=متن
    """

    serializer_class = MeetingListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()

        params = self.request.query_params
        status_param = params.get("status")
        search = params.get("search")

        if status_param:
            qs = qs.filter(status=status_param)

        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(body__icontains=search)
            )

        return qs.annotate(
            signers_count=Count("signers", distinct=True),
            signed_count=Count(
                "signers",
                filter=Q(signers__signed_at__isnull=False),
                distinct=True,
            ),
        )


class MeetingCreateApi(generics.CreateAPIView):

    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer
    permission_classes = (IsAuthenticated,)


class MeetingDetailApi(VisibleMeetingMixin, generics.RetrieveAPIView):

    serializer_class = MeetingDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "signers__user__employee_profile",
        )


class MeetingUpdateApi(VisibleMeetingMixin, generics.UpdateAPIView):

    serializer_class = MeetingUpdateSerializer
    permission_classes = (IsAuthenticated, IsMeetingOwnerOrAdmin)
    http_method_names = ("put", "patch", "options")


class MeetingDeleteApi(VisibleMeetingMixin, generics.DestroyAPIView):

    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated, IsMeetingOwnerOrAdmin)

    def perform_destroy(self, instance):
        if instance.status not in (
            Meeting.Status.DRAFT,
            Meeting.Status.CANCELED,
        ):
            raise ValidationError(
                "فقط پیش‌نویس یا صورت جلسه‌ی لغو شده قابل حذف است."
            )
        instance.delete()


class _ActionMixin(VisibleMeetingMixin):
    """
    ویوهای عملیاتی (ارسال برای امضا / لغو) که بدنه‌ی درخواست ندارند
    """

    serializer_class = serializers.Serializer
    permission_classes = (IsAuthenticated, IsMeetingOwnerOrAdmin)

    def respond(self, request, meeting):
        meeting = (
            Meeting.objects.select_related("created_by")
            .prefetch_related("signers__user__employee_profile")
            .get(pk=meeting.pk)
        )
        return Response(
            MeetingDetailSerializer(
                meeting,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )


class MeetingSendApi(_ActionMixin, generics.GenericAPIView):

    @extend_schema(request=None, responses=MeetingDetailSerializer)
    def post(self, request, pk):
        meeting = self.get_object()

        if not meeting.is_draft:
            raise ValidationError("این صورت جلسه قبلاً ارسال شده است.")

        if not meeting.signers.exists():
            raise ValidationError(
                "برای ارسال، حداقل یک امضاکننده لازم است."
            )

        meeting.send_for_signature()

        return self.respond(request, meeting)


class MeetingCancelApi(_ActionMixin, generics.GenericAPIView):

    @extend_schema(request=None, responses=MeetingDetailSerializer)
    def post(self, request, pk):
        meeting = self.get_object()

        if meeting.status not in (
            Meeting.Status.DRAFT,
            Meeting.Status.PENDING,
        ):
            raise ValidationError("این صورت جلسه قابل لغو نیست.")

        meeting.cancel()

        return self.respond(request, meeting)
