from django.db import models

from .purchase_employee import PurchaseProcessEmployee


class PurchaseProcessStep(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان مرحله"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="توضیحات"
    )
    order = models.PositiveIntegerField(
        verbose_name="ترتیب مرحله"
    )

    employees = models.ManyToManyField(
        PurchaseProcessEmployee,
        related_name="process_steps",
        blank=True,
        verbose_name="مسئولین مرحله"
    )

    class Meta:
        verbose_name = "مرحله فرآیند خرید"
        verbose_name_plural = "مراحل فرآیند خرید"
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                name="unique_purchase_process_step_order"
            )
        ]

    def __str__(self):
        return f"{self.order} - {self.title}"