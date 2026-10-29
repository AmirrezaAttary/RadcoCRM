from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0002_repair_document_file_and_step_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE document_documentstep
                ALTER COLUMN title DROP NOT NULL;
            """,
            reverse_sql="""
                ALTER TABLE document_documentstep
                ALTER COLUMN title SET NOT NULL;
            """,
        ),
    ]
