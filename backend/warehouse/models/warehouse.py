from django.db import models


class Warehouse(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="نام انبار"
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد انبار"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "انبار"
        verbose_name_plural = "انبارها"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"