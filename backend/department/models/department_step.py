from django.db import models

class DepartmentStep(models.Model):

    department = models.ForeignKey(
        "department.Department",
        on_delete=models.CASCADE,
        related_name="steps",
    )

    name = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    order = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["order"]