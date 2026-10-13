from django.conf import settings
from django.db import models

from accounts.models.employee import Employee
from warehouse.models.warehouse import Warehouse


class OrderTask(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "در حال انجام"
        COMPLETED = "completed", "تکمیل‌شده"
        CANCELLED = "cancelled", "لغو‌شده"

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="تسک اصلی",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        "warehouse.Product",
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="کالای سفارش",
        null=True,
        blank=True,
    )

    product_sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="قیمت فروش در زمان نهایی شدن سفارش",
    )

    quantity = models.FloatField(
        verbose_name="تعداد سفارش",
        null=True,
        blank=True,
    )

    completed_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="تعداد ارسال‌شده",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان تسک",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات تسک",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    case = models.ForeignKey(
        "tasks.Case",
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="پرونده",
    )

    department = models.ForeignKey(
        "department.Department",
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="دپارتمان",
    )

    current_step = models.ForeignKey(
        "department.DepartmentStep",
        on_delete=models.PROTECT,
        related_name="order_tasks",
        verbose_name="مرحله تسک",
    )

    assigned_employee = models.ManyToManyField(
        Employee,
        related_name="order_tasks",
        blank=True,
        verbose_name="کارمندان مسئول تسک",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_order_tasks",
        verbose_name="ایجادکننده تسک اصلی",
    )

    note = models.TextField(
        blank=True,
        verbose_name="توضیحات سفارش",
    )

    file = models.FileField(
        upload_to="warehouse/order_tasks/",
        null=True,
        blank=True,
        verbose_name="فایل سفارش",
    )

    performed_by = models.ForeignKey(
        "warehouse.WarehouseStaff",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="order_tasks",
        verbose_name="انجام‌دهنده",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name="وضعیت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "تسک سفارش انبار"
        verbose_name_plural = "تسک‌های سفارش انبار"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.title} | "
            f"{self.get_status_display()}"
        )


class OrderTaskItem(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESS = "success", "تأمین شد"
        FAILED = "failed", "تأمین نشد"

    order_task = models.ForeignKey(
        OrderTask,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="تسک سفارش",
    )

    product = models.ForeignKey(
        "warehouse.Product",
        on_delete=models.PROTECT,
        related_name="order_task_items",
        verbose_name="کالا",
    )

    quantity = models.FloatField(
        verbose_name="تعداد سفارش",
    )

    completed_quantity = models.FloatField(
        default=0,
        verbose_name="تعداد ارسال‌شده",
    )

    product_sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="قیمت فروش در زمان نهایی شدن",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت تأمین",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="دلیل عدم تأمین",
    )

    stock_transaction = models.OneToOneField(
        "warehouse.StockTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_task_item",
        verbose_name="تراکنش خروج انبار",
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
        verbose_name = "آیتم سفارش انبار"
        verbose_name_plural = "آیتم‌های سفارش انبار"
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "order_task",
                    "product",
                ],
                name="unique_order_task_product",
            ),
        ]

    def __str__(self):
        return (
            f"{self.order_task.title} | "
            f"{self.product.name} | "
            f"{self.quantity}"
        )


class OrderTaskDeadline(models.Model):

    order_task = models.OneToOneField(
        OrderTask,
        on_delete=models.CASCADE,
        related_name="deadline",
        verbose_name="تسک سفارش",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ شروع",
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="مهلت",
    )

    class Meta:
        verbose_name = "مهلت تسک سفارش"
        verbose_name_plural = "مهلت‌های تسک سفارش"

    def __str__(self):
        return f"Deadline for: {self.order_task.title}"


class OrderTaskAttachment(models.Model):

    order_task = models.ForeignKey(
        OrderTask,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="تسک سفارش",
    )

    performed_by = models.ForeignKey(
        "warehouse.WarehouseStaff",
        on_delete=models.PROTECT,
        related_name="order_task_attachments",
        verbose_name="انجام‌دهنده",
    )

    note = models.TextField(
        verbose_name="توضیحات اقدام",
    )

    file = models.FileField(
        upload_to="warehouse/order_tasks/attachments/",
        blank=True,
        null=True,
        verbose_name="فایل پیوست",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "پیوست تسک سفارش"
        verbose_name_plural = "پیوست‌های تسک سفارش"
        ordering = ["-created_at"]