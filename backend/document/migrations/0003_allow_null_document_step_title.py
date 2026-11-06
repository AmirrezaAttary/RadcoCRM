from django.db import migrations


class Migration(migrations.Migration):
    """
    No-op.

    DocumentStep.title is already nullable in 0001_initial. The old raw
    PostgreSQL-only SQL (ALTER COLUMN ... DROP NOT NULL) also fails on SQLite.
    """

    dependencies = [
        ("document", "0002_repair_document_file_and_step_fields"),
    ]

    operations = []
