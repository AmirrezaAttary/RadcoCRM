from accounts.models import User
from hr.models import Contract, ContractSignature


def is_admin(user):
    return bool(
        user
        and user.is_authenticated
        and user.type == User.UserType.ADMIN
    )


def visible_contracts(queryset, user):
    """
    ادمین (کارفرما) همه‌ی قراردادها را می‌بیند؛
    کارمند فقط قراردادهای ارسال‌شده‌ای که خودش باید امضا کند.
    """
    if is_admin(user):
        return queryset

    return queryset.exclude(status=Contract.Status.DRAFT).filter(
        pk__in=ContractSignature.objects.filter(
            employee__user=user,
        ).values("contract_id")
    )


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")
