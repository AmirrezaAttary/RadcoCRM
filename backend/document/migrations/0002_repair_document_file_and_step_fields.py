from django.db import migrations


class Migration(migrations.Migration):
    """
    No-op.

    0001_initial already creates DocumentFile.title, DocumentFile.step and a
    nullable DocumentStep.title, so re-adding them raised
    "duplicate column name: title". The migration name is kept so databases
    that already recorded it stay consistent.
    """

    dependencies = [
        ("document", "0001_initial"),
    ]

    operations = []
