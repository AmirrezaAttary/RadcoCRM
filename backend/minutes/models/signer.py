import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Signer(models.Model):
    """
    امضاکننده یا کاربر سیستم است (user) یا شخص بیرونی (full_name + phone_number).
    امضای شخص بیرونی با لینک اختصاصی (token) و بدون لاگین انجام می‌شود.
    """

    meeting = models.ForeignKey(
        "minutes.Meeting",
        on_delete=models.CASCADE,
        related_name="signers",
        verbose_name="صورت جلسه",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="meeting_signatures",
        verbose_name="امضا کننده (کاربر سیستم)",
    )

    # برای افراد بیرونی (وقتی user خالی است الزامی است)
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام و نام خانوادگی",
    )

    phone_number = models.CharField(
        max_length=11,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید با 09 شروع شود و 11 رقم باشد.",
            ),
        ],
        verbose_name="شماره موبایل",
    )

    role_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="سمت",
    )

    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    # لینک امضا برای افراد بیرونی
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    # تصویر امضا به صورت data URL (base64)
    signature_image = models.TextField(
        blank=True,
    )

    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان امضا",
    )

    signed_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    # هش متنی که امضا شده؛ باید با Meeting.content_hash برابر باشد
    signed_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("order", "id")
        verbose_name = "امضا کننده"
        verbose_name_plural = "امضا کننده‌ها"
        constraints = [
            # فقط برای کاربران سیستم؛ افراد بیرونی (user=NULL) محدود نمی‌شوند
            models.UniqueConstraint(
                fields=("meeting", "user"),
                name="unique_signer_per_meeting",
            ),
            models.CheckConstraint(
                check=Q(user__isnull=False) | ~Q(full_name=""),
                name="signer_has_user_or_full_name",
            ),
        ]

    def __str__(self):
        return f"{self.meeting_id} - {self.display_name}"

    @property
    def is_external(self):
        return self.user_id is None

    @property
    def is_signed(self):
        return self.signed_at is not None

    @property
    def display_name(self):
        if self.user_id is None:
            return self.full_name

        profile = getattr(self.user, "employee_profile", None)
        return (
            getattr(profile, "full_name", None)
            or self.full_name
            or self.user.username
        )

    def sign(self, signature_image, ip=None):
        self.signature_image = signature_image
        self.signed_at = timezone.now()
        self.signed_ip = ip
        self.signed_hash = self.meeting.content_hash
        self.save(
            update_fields=(
                "signature_image",
                "signed_at",
                "signed_ip",
                "signed_hash",
            )
        )
        self.meeting.refresh_status()
