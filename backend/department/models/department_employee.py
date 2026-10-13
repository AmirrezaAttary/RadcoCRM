from django.db import models


class DepartmentEmployee(models.Model):

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="department_memberships",
    )

    department = models.ForeignKey(
        "department.Department",
        on_delete=models.CASCADE,
        related_name="employee_memberships",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "department"],
                name="unique_employee_department",
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.full_name} | "
            f"{self.department.name} | "
        )