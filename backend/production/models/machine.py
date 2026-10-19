from django.db import models


class Machine(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name="نام دستگاه",
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="کد دستگاه",
    )

    std_production_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="تولید استاندارد در ساعت",
    )

    std_waste_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="ضایعات استاندارد در ساعت",
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
        verbose_name = "دستگاه"
        verbose_name_plural = "دستگاه‌ها"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"
