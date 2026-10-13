from pathlib import Path

from django.core.exceptions import ValidationError


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".word",
    ".txt",
    ".svg",
}


def validate_document_file(file):
    """
    Validate document file size and extension.
    """

    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            "File size must not exceed 10 MB."
        )

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_FILE_EXTENSIONS:
        allowed_extensions = ", ".join(
            sorted(ALLOWED_FILE_EXTENSIONS)
        )

        raise ValidationError(
            f"Invalid file extension. "
            f"Allowed extensions are: {allowed_extensions}."
        )