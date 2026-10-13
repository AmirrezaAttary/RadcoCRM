from django.db import models
from accounts.models.employee import Employee


class WarehouseStaff(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="warehouse_staff",
        verbose_name="کارمند"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ عضویت در انبار"
    )

    class Meta:
        verbose_name = "کارمند انبار"
        verbose_name_plural = "کارمندان انبار"

    def __str__(self):
        return self.employee.full_name
