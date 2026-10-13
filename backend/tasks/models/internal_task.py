# models/internal_task.py

from django.conf import settings
from django.db import models


class InternalTask(models.Model):

    class Status(models.TextChoices):
        WAITING = "waiting", "در انتظار"
        IN_PROGRESS = "in_progress", "در حال انجام"
        COMPLETED = "completed", "تکمیل شده"
        CANCELLED = "cancelled", "لغو شده"

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name="وضعیت",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="internal_tasks",
        verbose_name="مسئولان",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_internal_tasks",
        verbose_name="ایجادکننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تکمیل",
    )

    class Meta:
        verbose_name = "تسک درون‌سازمانی"
        verbose_name_plural = "تسک‌های درون‌سازمانی"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class InternalTaskRoutine(models.Model):

    task = models.OneToOneField(
        InternalTask,
        on_delete=models.CASCADE,
        related_name="routine",
        verbose_name="تسک",
    )

    start_at = models.DateTimeField(
        verbose_name="تاریخ و زمان شروع",
    )

    interval_days = models.PositiveIntegerField(
        verbose_name="فاصله تکرار بر حسب روز",
    )


    last_run_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین زمان اجرا",
    )

    next_run_at = models.DateTimeField(
        verbose_name="زمان اجرای بعدی",
    )

    is_active = models.BooleanField(
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
        verbose_name = "روتین تسک درون‌سازمانی"
        verbose_name_plural = "روتین‌های تسک‌های درون‌سازمانی"
        ordering = ["next_run_at"]

    def __str__(self):
        return f"Routine: {self.task.title}"

class InternalTaskDeadline(models.Model):
    task = models.OneToOneField(
        InternalTask,
        on_delete=models.CASCADE,
        related_name="deadline",
        verbose_name="تسک",
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ شروع")
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="مهلت")
    sms_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "مهلت تسک درون‌سازمانی"
        verbose_name_plural = "مهلت‌های تسک‌های درون‌سازمانی"

    def __str__(self):
        return f"Deadline for: {self.task.title}"
