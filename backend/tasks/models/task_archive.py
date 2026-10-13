from django.db import models


class TaskArchive(models.Model):

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

    case_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه پرونده",
    )

    case_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="عنوان پرونده",
    )

    case_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات پرونده",
    )

    case_created_by_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه ایجادکننده پرونده",
    )

    case_created_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="نام کاربری ایجادکننده پرونده",
    )

    case_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ایجاد پرونده",
    )

    case_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین بروزرسانی پرونده",
    )

    case_resources = models.JSONField(
        null=True,
        blank=True,
        verbose_name="منابع پرونده",
    )

    customer_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه مشتری",
    )

    customer_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام مشتری",
    )

    customer_job_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="سمت شغلی مشتری",
    )

    customer_phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="شماره تماس مشتری",
    )

    customer_company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام شرکت مشتری",
    )

    customer_address = models.TextField(
        null=True,
        blank=True,
        verbose_name="آدرس مشتری",
    )

    customer_source = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="منبع آشنایی مشتری",
    )

    customer_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات مشتری",
    )

    customer_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="وضعیت مشتری",
    )

    customer_status_display = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="نمایش وضعیت مشتری",
    )

    customer_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ایجاد مشتری",
    )

    customer_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین بروزرسانی مشتری",
    )

    department_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه دپارتمان",
    )

    department_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام دپارتمان",
    )

    department_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ترتیب دپارتمان",
    )

    department_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات دپارتمان",
    )

    current_step_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه مرحله فعلی",
    )

    current_step_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام مرحله فعلی",
    )

    current_step_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات مرحله فعلی",
    )

    current_step_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ترتیب مرحله فعلی",
    )

    department_steps_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Snapshot مراحل دپارتمان",
    )

    assigned_employees_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="کارمندان مسئول",
    )

    created_by_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه ایجادکننده تسک",
    )

    created_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="نام کاربری ایجادکننده تسک",
    )

    created_by_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام ایجادکننده تسک",
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

    step_logs_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="لاگ مراحل تسک",
    )

    deadlines_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="مهلت مراحل تسک",
    )

    attachments_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="پیوست‌های تسک",
    )

    customer_scores_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="امتیازات مشتری",
    )

    task_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ایجاد تسک",
    )

    task_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ بروزرسانی تسک",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تکمیل تسک",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        verbose_name="تاریخ آرشیو",
    )

    class Meta:
        verbose_name = "آرشیو تسک"
        verbose_name_plural = "آرشیو تسک‌ها"
        ordering = ["-archived_at"]

    def __str__(self):
        return f"Archive: {self.task_id} - {self.title}"