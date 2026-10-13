from django.db import models
from accounts.models.employee import Employee


class PurchaseProcessEmployee(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="purchase_process_employee",
        verbose_name="کارمند"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ عضویت"
    )

    class Meta:
        verbose_name = "کارمند فرآیند خرید"
        verbose_name_plural = "کارمندان فرآیند خرید"

    def __str__(self):
        return self.employee.full_name