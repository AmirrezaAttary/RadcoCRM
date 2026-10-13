# models/internal_task_attachment.py

import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from tasks.models.internal_task import InternalTask


ALLOWED_ATTACHMENT_EXTENSIONS = [
    "jpg", "jpeg", "png", "gif", "webp",
    "pdf", "doc", "docx", "txt",
]

MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024


def validate_attachment_size(file):
    if file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValidationError("حجم فایل نباید بیشتر از ۱۰ مگابایت باشد.")


def internal_task_attachment_upload_path(instance, filename):
    return f"internal_task_attachments/{instance.task_id}/{filename}"


class InternalTaskAttachment(models.Model):
    task = models.ForeignKey(
        InternalTask,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="تسک",
    )

    file = models.FileField(
        upload_to=internal_task_attachment_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=ALLOWED_ATTACHMENT_EXTENSIONS
            ),
            validate_attachment_size,
        ],
        blank=True,
        verbose_name="فایل",
    )

    original_file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام اصلی فایل",
    )

    note = models.TextField(
        blank=True,
        verbose_name="یادداشت",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="internal_task_attachments",
        verbose_name="آپلودکننده",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیوست تسک درون‌سازمانی"
        verbose_name_plural = "پیوست‌های تسک‌های درون‌سازمانی"
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_file_name or "پیوست بدون فایل"

    def save(self, *args, **kwargs):
        if not self.original_file_name and self.file:
            self.original_file_name = os.path.basename(self.file.name)

        super().save(*args, **kwargs)