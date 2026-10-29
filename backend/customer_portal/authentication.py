import hashlib
from datetime import timedelta
from functools import lru_cache

from django.contrib.auth.hashers import check_password, make_password
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import Token

from .models import CustomerPortalAccount


class PortalAccessToken(Token):
    """
    توکن مخصوص مشتری. token_type متفاوت با توکن کارمندان است،
    پس JWTAuthentication پیش‌فرض پروژه آن را رد می‌کند و برعکس.
    """

    token_type = "portal_access"
    lifetime = timedelta(hours=8)


def _password_stamp(account):
    # با تغییر رمز، توکن‌های قبلی خودبه‌خود باطل می‌شوند.
    return hashlib.sha256(account.password.encode()).hexdigest()[:16]


def issue_token(account):
    token = PortalAccessToken()
    token["account_id"] = account.pk
    token["pwd"] = _password_stamp(account)
    return token


@lru_cache(maxsize=1)
def _dummy_hash():
    return make_password("dummy-password-for-timing")


def verify_credentials(username, password):
    """
    مشتری فعال را برمی‌گرداند یا None.
    برای نام کاربری ناموجود هم هش بررسی می‌شود تا زمان پاسخ لو ندهد.
    """
    account = (
        CustomerPortalAccount.objects
        .select_related("customer")
        .filter(username=username)
        .first()
    )

    if account is None:
        check_password(password, _dummy_hash())
        return None

    if not account.check_password(password) or not account.is_active:
        return None

    return account


class PortalJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        header = get_authorization_header(request).split()

        if not header or header[0].lower() != b"bearer":
            return None

        if len(header) != 2:
            raise AuthenticationFailed("هدر Authorization نامعتبر است.")

        try:
            token = PortalAccessToken(header[1])
        except TokenError:
            raise AuthenticationFailed("توکن نامعتبر یا منقضی شده است.")

        account = (
            CustomerPortalAccount.objects
            .select_related("customer")
            .filter(pk=token.get("account_id"))
            .first()
        )

        if (
            account is None
            or not account.is_active
            or token.get("pwd") != _password_stamp(account)
        ):
            raise AuthenticationFailed("حساب کاربری نامعتبر یا غیرفعال است.")

        return (account, token)

    def authenticate_header(self, request):
        return 'Bearer realm="customer-portal"'


class PortalLoginThrottle(AnonRateThrottle):
    scope = "portal_login"
    rate = "10/min"


class IsPortalAccount(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, CustomerPortalAccount)
