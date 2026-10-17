from django.db import migrations, models


def assign_existing_staff_to_all_warehouses(apps, schema_editor):
    """
    برای اینکه بعد از دیپلوی هیچ انباردار فعلی قفل نشود،
    همه‌ی انباردارهای موجود به همه‌ی انبارهای موجود وصل می‌شوند.
    بعد از آن از پنل ادمین یا API برای هر انباردار فقط انبارهای خودش را نگه دارید.
    """
    WarehouseStaff = apps.get_model("warehouse", "WarehouseStaff")
    Warehouse = apps.get_model("warehouse", "Warehouse")

    warehouses = list(Warehouse.objects.all())

    for staff in WarehouseStaff.objects.all():
        staff.warehouses.set(warehouses)


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0005_alter_warehousetask_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="warehousestaff",
            name="warehouses",
            field=models.ManyToManyField(
                blank=True,
                related_name="staff_members",
                to="warehouse.warehouse",
                verbose_name="انبارهای مجاز",
            ),
        ),
        migrations.RunPython(
            assign_existing_staff_to_all_warehouses,
            migrations.RunPython.noop,
        ),
    ]
