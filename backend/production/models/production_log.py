from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

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

    # ساعت شروع و پایان کار. اگر پایان کوچک‌تر یا مساوی شروع باشد
    # یعنی شیفت از نیمه‌شب گذشته و پایان مربوط به روز بعد است.
    # برای رکوردهای قدیمی که قبل از این فیلدها ثبت شده‌اند خالی است.
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="ساعت شروع",
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="ساعت پایان",
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

    @staticmethod
    def hours_between(start_time, end_time):
        """
        فاصله‌ی دو ساعت به‌صورت ساعت اعشاری (دو رقم اعشار).
        اگر پایان <= شروع باشد، پایان در روز بعد فرض می‌شود.
        """
        start = datetime.combine(date.min, start_time)
        end = datetime.combine(date.min, end_time)

        if end <= start:
            end += timedelta(days=1)

        hours = Decimal((end - start).total_seconds()) / Decimal(3600)
        return hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def crosses_midnight(self):
        return bool(
            self.start_time
            and self.end_time
            and self.end_time <= self.start_time
        )

    def save(self, *args, **kwargs):
        # اگر ساعت شروع و پایان داده شده باشد، ساعت کار از روی آن‌ها
        # محاسبه می‌شود تا یک منبع واحد برای همه‌ی گزارش‌ها داشته باشیم.
        if self.start_time and self.end_time:
            self.hours_worked = self.hours_between(
                self.start_time, self.end_time,
            )

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
