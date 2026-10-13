from django.conf import settings
from django.db import models

from .validators import validate_document_file


class Document(models.Model):
    title = models.CharField(
        max_length=255,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documents",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title


class DocumentFile(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="files",
    )

    file = models.FileField(
        upload_to="documents/",
        validators=[validate_document_file],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.file.name


class DocumentStep(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    order = models.PositiveIntegerField()

    title = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "order"],
                name="unique_document_step_order",
            ),
        ]

    def __str__(self):
        return f"{self.document.title} - Step {self.order}"