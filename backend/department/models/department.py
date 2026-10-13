from django.db import models


class Department(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    order = models.PositiveIntegerField(
        unique=True,
        verbose_name="ترتیب مرحله"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name