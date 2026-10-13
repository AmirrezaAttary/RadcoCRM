from django.db import models


class InternalTaskArchive(models.Model):
    task_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه تسک",
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="عنوان تسک",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات تسک",
    )
    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="وضعیت نهایی",
    )
    task_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ایجاد تسک",
    )
    task_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین بروزرسانی تسک",
    )
    execution_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان شروع این اجرا",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تکمیل",
    )
    assigned_employees_snapshot = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Snapshot مسئولان تسک",
    )
    deadline_snapshot = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name="Snapshot مهلت تسک",
    )
    attachments_snapshot = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Snapshot پیوست‌ها",
    )
    created_by_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه ایجادکننده",
    )
    created_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="نام کاربری ایجادکننده",
    )
    created_by_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام ایجادکننده",
    )
    final_action_by_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه انجام‌دهنده عملیات نهایی",
    )
    final_action_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="نام کاربری انجام‌دهنده عملیات نهایی",
    )
    final_action_by_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام انجام‌دهنده عملیات نهایی",
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        verbose_name="تاریخ آرشیو",
    )

    class Meta:
        verbose_name = "آرشیو تسک درون‌سازمانی"
        verbose_name_plural = "آرشیو تسک‌های درون‌سازمانی"
        ordering = ["-archived_at"]

    def __str__(self):
        return f"InternalTask Archive: {self.task_id} - {self.title}"
