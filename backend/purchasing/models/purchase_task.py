from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from warehouse.models.product import Product
from .purchase_step import PurchaseProcessStep
from .purchase_employee import PurchaseProcessEmployee
from warehouse.models.warehouse import Warehouse


class PurchaseTask(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        IN_PROGRESS = "in_progress", "در حال انجام"
        COMPLETED = "completed", "تکمیل شده"
        CANCELLED = "cancelled", "لغو شده"

    class Source(models.TextChoices):
        SYSTEM = "system", "سیستم"
        MANUAL = "manual", "دستی"
        INITIAL = "initial", "موجودی اولیه"

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="purchase_tasks",
        null=True,
        blank=True,
        verbose_name="انبار",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_tasks",
        verbose_name="کالا"
    )

    process_step = models.ForeignKey(
        PurchaseProcessStep,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="مرحله فرآیند"
    )

    minimum_stock = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداقل موجودی"
    )

    maximum_stock = models.FloatField(
        null=True,
        blank=True,
        verbose_name="حداکثر موجودی"
    )

    quantity_after = models.FloatField(
        null=True,
        blank=True,
        verbose_name="موجودی پس از خروج"
    )

    purchase_quantity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="مقدار مورد نیاز خرید"
    )

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.SYSTEM,
        verbose_name="منبع ایجاد"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_purchase_tasks",
        verbose_name="ایجاد کننده"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "تسک خرید"
        verbose_name_plural = "تسک‌های خرید"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.purchase_quantity}"


class PurchaseTaskAttachment(models.Model):

    class Type(models.TextChoices):
        TASK = "task", "تسک"
        ADVANCE = "advance", "پیشرفت"
        REVERT = "revert", "بازگشت"

    task = models.ForeignKey(
        PurchaseTask,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="تسک خرید"
    )

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name="نوع پیوست"
    )

    process_step = models.ForeignKey(
        PurchaseProcessStep,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_task_attachments",
        verbose_name="مرحله فرآیند"
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات"
    )

    file = models.FileField(
        upload_to="purchasing/task_attachments/",
        null=True,
        blank=True,
        verbose_name="فایل"
    )

    created_by = models.ForeignKey(
        PurchaseProcessEmployee,
        on_delete=models.PROTECT,
        related_name="purchase_task_attachments",
        verbose_name="ایجاد کننده"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "پیوست تسک خرید"
        verbose_name_plural = "پیوست‌های تسک خرید"
        ordering = ["-created_at"]

    def clean(self):
        if self.type == self.Type.TASK and self.process_step is not None:
            raise ValidationError({
                "process_step":
                    "برای پیوست نوع تسک، مرحله فرآیند نباید مشخص شود."
            })

        if self.type in [self.Type.ADVANCE, self.Type.REVERT]:
            if self.process_step is None:
                raise ValidationError({
                    "process_step":
                        "برای پیوست Advance یا Revert، مرحله فرآیند الزامی است."
                })

    def __str__(self):
        return f"{self.task} - {self.get_type_display()}"