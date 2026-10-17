from rest_framework.permissions import BasePermission

from django.db.models import Q

from minutes.models import Meeting, Signer


def visible_meetings(queryset, user):
    """
    ادمین همه‌ی صورت‌جلسه‌ها را می‌بیند؛
    بقیه فقط مواردی که خودشان ساخته‌اند یا امضاکننده‌ی آن هستند.
    """
    if user.is_staff:
        return queryset

    # با subquery (نه join) تا شمارش امضاکننده‌ها در annotate خراب نشود
    return queryset.filter(
        Q(created_by=user)
        | Q(pk__in=Signer.objects.filter(user=user).values("meeting_id"))
    )


class IsMeetingOwnerOrAdmin(BasePermission):
    """
    object-level: روی Meeting یا هر آبجکتی که فیلد meeting دارد (مثل Signer)
    """

    message = "فقط ایجاد کننده‌ی صورت جلسه یا ادمین مجاز است."

    def has_object_permission(self, request, view, obj):
        meeting = obj if isinstance(obj, Meeting) else obj.meeting

        return bool(
            request.user.is_staff
            or meeting.created_by_id == request.user.id
        )


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")
