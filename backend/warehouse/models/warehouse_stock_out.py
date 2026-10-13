from django.db import models

from warehouse.models.product import Product
from warehouse.models.warehouse import Warehouse
from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.models.warehouse_process import StockTransaction


class WarehouseStockOut(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESS = "success", "موفق"
        PARTIAL = "partial", "موفق جزئی"
        FAILED = "failed", "ناموفق"

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_out_invoices",
        verbose_name="انبار",
    )

    performed_by = models.ForeignKey(
        WarehouseStaff,
        on_delete=models.PROTECT,
        related_name="stock_out_invoices",
        verbose_name="انجام‌دهنده",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    file = models.FileField(
        upload_to="warehouse/stock_out/",
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

    class Meta:
        verbose_name = "فاکتور خروج انبار"
        verbose_name_plural = "فاکتورهای خروج انبار"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"فاکتور خروج #{self.pk} | "
            f"{self.warehouse.name}"
        )


class WarehouseStockOutItem(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESS = "success", "موفق"
        FAILED = "failed", "ناموفق"

    stock_out = models.ForeignKey(
        WarehouseStockOut,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="فاکتور خروج",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_out_items",
        verbose_name="کالا",
    )

    quantity = models.FloatField(
        verbose_name="مقدار خروج",
    )

    reason = models.CharField(
        max_length=20,
        choices=StockTransaction.StockOutReason.choices,
        default=StockTransaction.StockOutReason.SALE,
        verbose_name="دلیل خروج",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    quantity_before = models.FloatField(
        null=True,
        blank=True,
        verbose_name="موجودی قبل از خروج",
    )

    quantity_after = models.FloatField(
        null=True,
        blank=True,
        verbose_name="موجودی بعد از خروج",
    )

    stock_transaction = models.OneToOneField(
        StockTransaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="stock_out_item",
        verbose_name="تراکنش انبار",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="علت عدم موفقیت",
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
        verbose_name = "قلم فاکتور خروج"
        verbose_name_plural = "اقلام فاکتور خروج"
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=["stock_out", "product"],
                name="unique_stock_out_product",
            )
        ]

    def __str__(self):
        return (
            f"{self.stock_out_id} | "
            f"{self.product.name} | "
            f"{self.quantity}"
        )