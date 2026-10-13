from django.db import models

from purchasing.models.purchase_task import PurchaseTask
from quality_control.models.quality_control import QualityControl
from warehouse.models.product import Product
from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.models.warehouse import Warehouse


class WarehouseTask(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        IN_PROGRESS = "in_progress", "در حال انجام"
        COMPLETED = "completed", "تکمیل شده"
        CANCELLED = "cancelled", "لغو شده"

    purchase_task = models.ForeignKey(
        PurchaseTask,
        on_delete=models.PROTECT,
        related_name="warehouse_tasks",
        verbose_name="تسک خرید",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="warehouse_tasks",
        null=True,
        blank=True,
        verbose_name="انبار",
    )

    quality_control = models.OneToOneField(
        QualityControl,
        on_delete=models.PROTECT,
        related_name="warehouse_task",
        verbose_name="کنترل کیفیت",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="warehouse_tasks",
        verbose_name="کالا",
    )

    expected_quantity = models.FloatField(
        verbose_name="مقدار مورد انتظار",
    )

    received_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="مقدار دریافت شده",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    assigned_to = models.ForeignKey(
        WarehouseStaff,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="warehouse_tasks",
        verbose_name="انباردار",
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    file = models.FileField(
        upload_to="warehouse/tasks/",
        null=True,
        blank=True,
        verbose_name="فایل",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تکمیل",
    )

    class Meta:
        verbose_name = "تسک انبار"
        verbose_name_plural = "تسک‌های انبار"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.expected_quantity}"