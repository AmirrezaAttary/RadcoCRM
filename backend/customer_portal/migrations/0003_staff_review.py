from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_portal", "0002_order_task_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerorder",
            name="staff_note",
            field=models.TextField(blank=True, default="", verbose_name="توضیحات کارمند"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customerorder",
            name="handled_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="handled_customer_orders", to=settings.AUTH_USER_MODEL, verbose_name="بررسی\u200cکننده"),
        ),
        migrations.AlterField(
            model_name="customerorder",
            name="status",
            field=models.CharField(choices=[("pending", "در انتظار تأیید کارمند"), ("in_warehouse", "در انتظار تأیید انباردار"), ("confirmed", "تأیید شد"), ("partial", "تأیید جزئی"), ("rejected", "رد شد / تأمین نشد")], default="pending", max_length=20, verbose_name="وضعیت"),
        ),
    ]
