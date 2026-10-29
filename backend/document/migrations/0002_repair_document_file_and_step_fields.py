from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AddField(
                    model_name="documentfile",
                    name="title",
                    field=models.CharField(
                        max_length=255,
                        null=True,
                        blank=True,
                    ),
                ),
                migrations.AddField(
                    model_name="documentfile",
                    name="step",
                    field=models.ForeignKey(
                        to="document.documentstep",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        null=True,
                        blank=True,
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="documentfile",
                    name="title",
                    field=models.CharField(
                        max_length=255,
                        null=True,
                        blank=True,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="documentstep",
            name="title",
            field=models.CharField(
                max_length=255,
                null=True,
                blank=True,
            ),
        ),
    ]
