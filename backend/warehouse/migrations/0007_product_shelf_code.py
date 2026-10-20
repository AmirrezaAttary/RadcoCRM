from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0006_warehousestaff_warehouses"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="shelf_code",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                max_length=50,
                verbose_name="کد قفسه",
            ),
        ),
    ]
