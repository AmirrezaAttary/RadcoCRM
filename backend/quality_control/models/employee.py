from django.db import models

from accounts.models.user import User


class QualityControlEmployee(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="quality_control_employee",
        verbose_name="کاربر",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "کارمند کنترل کیفیت"
        verbose_name_plural = "کارمندان کنترل کیفیت"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username
