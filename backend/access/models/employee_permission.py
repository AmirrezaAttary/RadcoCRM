from django.db import models


class EmployeePermission(models.Model):

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="permission_assignments",
    )

    permission = models.ForeignKey(
        "access.Permission",
        on_delete=models.CASCADE,
        related_name="employee_assignments",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "permission"],
                name="unique_employee_permission",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee} | "
            f"{self.permission.code}"
        )