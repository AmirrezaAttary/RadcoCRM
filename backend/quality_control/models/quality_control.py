from django.db import models

from purchasing.models.purchase_task import PurchaseTask
from quality_control.models.employee import QualityControlEmployee


class QualityControl(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    purchase_task = models.ForeignKey(
        PurchaseTask,
        on_delete=models.PROTECT,
        related_name="quality_controls",
        verbose_name="تسک خرید",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    note = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات",
    )

    file = models.FileField(
        upload_to="quality_control/files/",
        null=True,
        blank=True,
        verbose_name="فایل",
    )

    checked_by = models.ForeignKey(
        QualityControlEmployee, 
        on_delete=models.PROTECT, 
        null=True, blank=True, 
        related_name="checked_quality_controls",
        verbose_name="بررسی کننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    checked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ بررسی",
    )

    class Meta:
        verbose_name = "کنترل کیفیت"
        verbose_name_plural = "کنترل‌های کیفیت"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.purchase_task} - "
            f"{self.get_status_display()}"
        )