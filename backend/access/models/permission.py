from django.db import models


class Permission(models.Model):

    resource = models.CharField(
        max_length=100,
    )

    action = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=255,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
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
                fields=["resource", "action"],
                name="unique_permission_resource_action",
            )
        ]

    def __str__(self):
        return self.code