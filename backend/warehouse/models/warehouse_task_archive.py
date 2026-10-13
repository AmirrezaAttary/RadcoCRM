from django.db import models


class WarehouseTaskArchive(models.Model):
    warehouse_task = models.ForeignKey(
        "warehouse.WarehouseTask",
        on_delete=models.PROTECT,
        related_name="archives",
        null=True,
        blank=True,
        verbose_name="تسک انبار",
    )

    purchase_task_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه تسک خرید",
    )

    purchase_task_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="عنوان تسک خرید",
    )

    purchase_task_source = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="نوع تسک خرید",
    )

    purchase_task_created_by_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه ایجاد کننده تسک خرید",
    )

    purchase_task_created_by_employee_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه کارمند ایجاد کننده",
    )

    purchase_task_created_by_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام ایجاد کننده تسک خرید",
    )

    quality_control_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه کنترل کیفیت",
    )

    quality_control_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="عنوان کنترل کیفیت",
    )

    warehouse_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه انبار",
    )

    warehouse_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="نام انبار",
    )

    warehouse_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="کد انبار",
    )

    product_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه کالا",
    )

    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام کالا",
    )

    expected_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="مقدار مورد انتظار",
    )

    received_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="مقدار دریافت شده",
    )

    minimum_stock = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداقل موجودی در زمان آرشیو",
    )

    maximum_stock = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداکثر موجودی در زمان آرشیو",
    )

    quantity_before = models.FloatField(
        null=True,
        blank=True,
        verbose_name="موجودی قبل از تغییر",
    )

    quantity_after = models.FloatField(
        null=True,
        blank=True,
        verbose_name="موجودی بعد از تغییر",
    )

    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="وضعیت نهایی",
    )

    assigned_to_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه انباردار",
    )

    assigned_to_employee_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه کارمند",
    )

    assigned_to_full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام انباردار",
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    file = models.FileField(
        upload_to="warehouse/tasks/archive/",
        null=True,
        blank=True,
        verbose_name="فایل",
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

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تکمیل",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        verbose_name="تاریخ آرشیو",
    )

    class Meta:
        verbose_name = "آرشیو تسک انبار"
        verbose_name_plural = "آرشیو تسک‌های انبار"
        ordering = ["-archived_at"]

    def __str__(self):
        return f"Archive: {self.warehouse_task_id}"