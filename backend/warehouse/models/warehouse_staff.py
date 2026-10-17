from django.db import models
from accounts.models.employee import Employee
from warehouse.models.warehouse import Warehouse


class WarehouseStaff(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="warehouse_staff",
        verbose_name="کارمند"
    )
    warehouses = models.ManyToManyField(
        Warehouse,
        blank=True,
        related_name="staff_members",
        verbose_name="انبارهای مجاز"
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

    def can_access_warehouse(self, warehouse):
        """warehouse می‌تواند شیء Warehouse یا id باشد."""
        warehouse_id = getattr(warehouse, "pk", warehouse)
        if warehouse_id is None:
            return False
        return self.warehouses.filter(pk=warehouse_id).exists()
