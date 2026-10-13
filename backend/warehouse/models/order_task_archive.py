from django.db import models


class OrderTaskArchive(models.Model):

    order_task = models.ForeignKey(
        "warehouse.OrderTask",
        on_delete=models.PROTECT,
        related_name="archives",
        null=True,
        blank=True,
        verbose_name="تسک سفارش",
    )


    task_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="شناسه تسک اصلی",
    )

    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="وضعیت نهایی",
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
        verbose_name="شناسه کالای قدیمی",
    )

    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="نام کالای قدیمی",
    )

    product_sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="قیمت فروش کالای قدیمی",
    )

    quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="تعداد سفارش قدیمی",
    )

    completed_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="تعداد ارسال‌شده قدیمی",
    )

    items = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="اقلام سفارش",
    )

    case = models.JSONField(
        null=True,
        blank=True,
        verbose_name="پرونده",
    )

    customer = models.JSONField(
        null=True,
        blank=True,
        verbose_name="مشتری",
    )

    department = models.JSONField(
        null=True,
        blank=True,
        verbose_name="دپارتمان",
    )

    current_step = models.JSONField(
        null=True,
        blank=True,
        verbose_name="مرحله",
    )

    created_by = models.JSONField(
        null=True,
        blank=True,
        verbose_name="ایجادکننده",
    )

    performed_by = models.JSONField(
        null=True,
        blank=True,
        verbose_name="انجام‌دهنده",
    )

    assigned_employees = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="کارمندان مسئول",
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات سفارش",
    )

    completion_note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات نهایی",
    )

    file = models.FileField(
        upload_to="warehouse/order_tasks/archive/",
        null=True,
        blank=True,
        verbose_name="فایل سفارش",
    )

    order_task_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ ایجاد تسک",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True,
        verbose_name="تاریخ آرشیو",
    )

    class Meta:
        verbose_name = "آرشیو تسک سفارش"
        verbose_name_plural = "آرشیو تسک‌های سفارش"
        ordering = ["-archived_at"]

    def __str__(self):
        return f"Archive: {self.order_task_id}"