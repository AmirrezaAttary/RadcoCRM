from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Note(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
        verbose_name=_("user"),
    )

    description = models.TextField(
        verbose_name=_("description"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("note")
        verbose_name_plural = _("notes")

    def __str__(self):
        return f"Note #{self.pk} - {self.user.username}"