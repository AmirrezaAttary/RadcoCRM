from django.db import models
from django.utils import timezone

from .product import Product, UNIT_TYPE
from .warehouse import Warehouse


class InventoryStock(models.Model):

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventory_stocks",
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_stocks",
        verbose_name="کالا",
    )

    initial_quantity = models.FloatField(
        verbose_name="موجودی اول دوره"
    )

    current_quantity = models.FloatField(
        verbose_name="موجودی جاری"
    )

    minimum_stock = models.FloatField(
        default=0,
        verbose_name="حداقل موجودی"
    )

    maximum_stock = models.FloatField(
        default=0,
        verbose_name="حداکثر موجودی"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت اول دوره"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "موجودی انبار"
        verbose_name_plural = "موجودی‌های انبار"
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"],
                name="unique_warehouse_product_stock"
            )
        ]

    def __str__(self):
        unit_label = self._get_unit_label()

        return (
            f"{self.warehouse.name} | "
            f"{self.product.name} | "
            f"موجودی: {self.current_quantity} {unit_label}"
        )

    def _get_unit_label(self):
        labels = {
            UNIT_TYPE.COUNT: "عدد",
            UNIT_TYPE.WEIGHT: "وزن",
            UNIT_TYPE.VOLUME: "حجم",
            UNIT_TYPE.DIMENSION: "ابعاد",
            UNIT_TYPE.AREA: "مساحت",
        }

        return labels.get(self.product.unit_type, "")


class StockTransaction(models.Model):

    class TransactionType(models.TextChoices):
        STOCK_IN = "stock_in", "ورودی کالا"
        STOCK_OUT = "stock_out", "خروجی کالا"
        INITIAL = "initial", "موجودی اول دوره"

    class StockOutReason(models.TextChoices):
        SALE = "sale", "فروش"
        DAMAGE = "damage", "خرابی / ضایعات"
        TRANSFER = "transfer", "انتقال"
        OTHER = "other", "سایر"

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_transactions",
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="کالا"
    )

    performed_by = models.ForeignKey(
        "warehouse.WarehouseStaff",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="transactions",
        verbose_name="انجام‌دهنده"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name="نوع تراکنش"
    )

    quantity_changed = models.FloatField(
        verbose_name="مقدار تغییر"
    )

    quantity_before = models.FloatField(
        verbose_name="موجودی قبل از تغییر"
    )

    quantity_after = models.FloatField(
        verbose_name="موجودی بعد از تغییر"
    )

    stock_out_reason = models.CharField(
        max_length=20,
        choices=StockOutReason.choices,
        null=True,
        blank=True,
        verbose_name="دلیل خروج"
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات"
    )

    transaction_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ تراکنش"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "تراکنش انبار"
        verbose_name_plural = "تراکنش‌های انبار"
        ordering = ["-transaction_date"]

    def __str__(self):
        return (
            f"{self.get_transaction_type_display()} | "
            f"{self.warehouse.name} | "
            f"{self.product.name} | "
            f"{self.quantity_before} ← {self.quantity_after}"
        )