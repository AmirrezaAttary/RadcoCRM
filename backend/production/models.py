# production/models.py
from django.conf import settings
from django.db import models


class Machine(models.Model):
    name = models.CharField("نام دستگاه", max_length=100)
    code = models.CharField("کد دستگاه", max_length=30, unique=True)
    std_production_per_hour = models.DecimalField(
        "تولید استاندارد در ساعت", max_digits=10, decimal_places=2)
    std_waste_per_hour = models.DecimalField(
        "ضایعات استاندارد در ساعت", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("فعال", default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Operator(models.Model):
    # اگر مدل کارمند/کاربر دارید، به جای این مدل به همون ForeignKey بزنید
    full_name = models.CharField("نام اپراتور", max_length=100)
    is_active = models.BooleanField("فعال", default=True)

    def __str__(self):
        return self.full_name


class ProductionLog(models.Model):
    date = models.DateField("تاریخ")
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT,
                                 related_name="logs", verbose_name="اپراتور")
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT,
                                related_name="logs", verbose_name="دستگاه")
    hours_worked = models.DecimalField("ساعت کار", max_digits=5, decimal_places=2)
    produced_qty = models.PositiveIntegerField("تعداد تولید")
    waste_qty = models.PositiveIntegerField("تعداد ضایعات", default=0)
    note = models.CharField("توضیحات", max_length=255, blank=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "operator", "machine"],
                name="uniq_log_per_day_operator_machine"),
        ]

    @property
    def expected_production(self):
        return self.hours_worked * self.machine.std_production_per_hour

    @property
    def expected_waste(self):
        return self.hours_worked * self.machine.std_waste_per_hour

    @property
    def efficiency(self):
        exp = self.expected_production
        return round(self.produced_qty / exp * 100, 1) if exp else None