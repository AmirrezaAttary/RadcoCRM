from django.db import models


class Score(models.Model):
    class Action(models.TextChoices):
        DEDUCT = "deduct", "کسر امتیاز"
        ADD = "add", "افزایش امتیاز"

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.PROTECT,
        related_name="scores",
        verbose_name="کارمند",
    )

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="score_logs",
        verbose_name="تسک",
        null=True,
        blank=True,
    )

    department_step = models.ForeignKey(
        "department.DepartmentStep",
        on_delete=models.PROTECT,
        related_name="score_logs",
        verbose_name="مرحله",
        null=True,
        blank=True,
    )

    order_task = models.ForeignKey(
        "warehouse.OrderTask",
        on_delete=models.PROTECT,
        related_name="score_logs",
        verbose_name="تسک سفارش انبار",
        null=True,
        blank=True,
    )

    amount = models.PositiveIntegerField(
        verbose_name="مقدار کسر امتیاز",
    )

    reason = models.TextField(
        verbose_name="دلیل کاهش امتیاز",
    )

    overdue_period = models.PositiveIntegerField(
        verbose_name="دوره تأخیر ۲۴ ساعته",
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=10,
        choices=Action.choices,
        default=Action.DEDUCT,
        verbose_name="نوع تغییر امتیاز",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "task",
                    "department_step",
                    "overdue_period",
                ],
                name="unique_task_score_per_overdue_period",
            ),

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "order_task",
                    "overdue_period",
                ],
                name="unique_order_task_score_per_overdue_period",
            ),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        source = self.task or self.order_task

        return (
            f"{self.employee} - "
            f"{source} - "
            f"{self.amount}"
        )