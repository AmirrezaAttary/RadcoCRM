import hashlib

from django.conf import settings
from django.db import models


class Meeting(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING = "pending", "در انتظار امضا"
        SIGNED = "signed", "امضا شده"
        CANCELED = "canceled", "لغو شده"

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
    )

    held_at = models.DateTimeField(
        verbose_name="زمان جلسه",
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="مکان",
    )

    body = models.TextField(
        verbose_name="متن صورت جلسه",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    # هش متن در لحظه‌ی ارسال برای امضا؛ متن بعد از آن قفل می‌شود
    content_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_meetings",
        verbose_name="ایجاد کننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-held_at", "-id")
        verbose_name = "صورت جلسه"
        verbose_name_plural = "صورت جلسه‌ها"

    def __str__(self):
        return self.title

    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT

    def compute_hash(self):
        raw = f"{self.title}|{self.held_at.isoformat()}|{self.location}|{self.body}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def send_for_signature(self):
        self.content_hash = self.compute_hash()
        self.status = self.Status.PENDING
        self.save(update_fields=("content_hash", "status", "updated_at"))

    def cancel(self):
        self.status = self.Status.CANCELED
        self.save(update_fields=("status", "updated_at"))

    def refresh_status(self):
        if (
            self.status == self.Status.PENDING
            and not self.signers.filter(signed_at__isnull=True).exists()
        ):
            self.status = self.Status.SIGNED
            self.save(update_fields=("status", "updated_at"))
