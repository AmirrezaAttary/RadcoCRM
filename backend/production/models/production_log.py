from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models.employee import Employee
from production.models.machine import Machine


class ProductionLog(models.Model):
    """
    ثبت روزانه: یک کارمند، در یک روز، روی یک دستگاه، چند ساعت کار کرده
    و چقدر تولید و ضایعات داشته است.
    """

    date = models.DateField(
        verbose_name="تاریخ",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="production_logs",
        verbose_name="اپراتور",
    )

    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="production_logs",
        verbose_name="دستگاه",
    )

    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("24")),
        ],
        verbose_name="ساعت کار",
    )

    produced_qty = models.PositiveIntegerField(
        verbose_name="تعداد تولید",
    )

    waste_qty = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد ضایعات",
    )

    # استانداردِ دستگاه در لحظه ثبت؛ تا با تغییر استاندارد دستگاه،
    # گزارش‌های گذشته تغییر نکنند.
    std_production_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="تولید استاندارد در ساعت (زمان ثبت)",
    )

    std_waste_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="ضایعات استاندارد در ساعت (زمان ثبت)",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توضیحات",
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
        verbose_name = "ثبت تولید"
        verbose_name_plural = "ثبت‌های تولید"
        ordering = ["-date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "employee", "machine"],
                name="uniq_production_log_date_employee_machine",
            ),
        ]

    def __str__(self):
        return f"{self.date} - {self.employee} - {self.machine}"

    def save(self, *args, **kwargs):
        # فقط هنگام ایجاد، استاندارد فعلی دستگاه کپی می‌شود
        if self._state.adding:
            self.std_production_per_hour = self.machine.std_production_per_hour
            self.std_waste_per_hour = self.machine.std_waste_per_hour
        super().save(*args, **kwargs)

    @property
    def expected_production(self):
        return self.hours_worked * self.std_production_per_hour

    @property
    def expected_waste(self):
        return self.hours_worked * self.std_waste_per_hour

    @property
    def efficiency(self):
        expected = self.expected_production
        if not expected:
            return None
        return round(self.produced_qty / expected * 100, 1)
