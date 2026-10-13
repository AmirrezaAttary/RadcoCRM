from django.conf import settings
from django.db import models


class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    full_name = models.CharField(
        max_length=255,
        null=True, 
        blank=True,
    )

    avatar = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True,
    )

    email = models.EmailField(
        null=True,
        blank=True,
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.full_name