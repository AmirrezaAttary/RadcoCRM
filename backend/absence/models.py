from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


ALLOWED_ABSENCE_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".txt",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}

MAX_ABSENCE_ATTACHMENT_SIZE = 10 * 1024 * 1024 


def validate_absence_attachment_extension(value):
    extension = Path(value.name).suffix.lower()

    if extension not in ALLOWED_ABSENCE_EXTENSIONS:
        allowed_extensions = ", ".join(
            sorted(ALLOWED_ABSENCE_EXTENSIONS)
        )

        raise ValidationError(
            f"پسوند فایل مجاز نیست. پسوندهای مجاز: {allowed_extensions}"
        )


def validate_absence_attachment_size(value):
    if value.size > MAX_ABSENCE_ATTACHMENT_SIZE:
        raise ValidationError(
            "حجم فایل نمی‌تواند بیشتر از 10 مگابایت باشد."
        )


class Absence(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="absences",
        verbose_name="کاربر",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_absences",
        verbose_name="بررسی کننده",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات",
    )

    start_date = models.DateTimeField(
        verbose_name="شروع مرخصی",
    )

    end_date = models.DateTimeField(
        verbose_name="پایان مرخصی",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        db_table = "absence"
        ordering = ["-created_at"]
        verbose_name = "مرخصی"
        verbose_name_plural = "مرخصی‌ها"

    def __str__(self):
        return f"{self.user} - {self.title}"


class AbsenceAttachment(models.Model):

    absence = models.ForeignKey(
        Absence,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="مرخصی",
    )

    file = models.FileField(
        upload_to="absence/attachments/%Y/%m/%d/",
        validators=[
            validate_absence_attachment_extension,
            validate_absence_attachment_size,
        ],
        verbose_name="فایل",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        db_table = "absence_attachment"
        ordering = ["-created_at"]
        verbose_name = "پیوست مرخصی"
        verbose_name_plural = "پیوست‌های مرخصی"

    def __str__(self):
        return f"{self.absence.title} - {self.file.name}"