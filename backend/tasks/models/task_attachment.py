import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from .tasks import *


ALLOWED_ATTACHMENT_EXTENSIONS = [
    "jpg", "jpeg", "png", "gif", "webp",
    "pdf", "doc", "docx", "txt",
]

MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_attachment_size(file):
    if file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValidationError("حجم فایل نباید بیشتر از ۱۰ مگابایت باشد.")


def task_attachment_upload_path(instance, filename):
    if instance.task_id:
        return f"task_attachments/tasks/{instance.task_id}/{filename}"
    return f"task_attachments/step_logs/{instance.task_step_log_id}/{filename}"


class TaskAttachment(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="تسک",
    )
    task_step_log = models.ForeignKey(
        TaskStepLog,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="لاگ مرحله",
    )

    file = models.FileField(
        upload_to=task_attachment_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_ATTACHMENT_EXTENSIONS),
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

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_attachments",
        verbose_name="آپلودکننده",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیوست تسک"
        verbose_name_plural = "پیوست‌های تسک"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(task__isnull=False, task_step_log__isnull=True)
                    | models.Q(task__isnull=True, task_step_log__isnull=False)
                ),
                name="attachment_belongs_to_task_xor_steplog",
            )
        ]

    def __str__(self):
        return self.original_file_name

    def save(self, *args, **kwargs):
        if not self.original_file_name and self.file:
            self.original_file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)