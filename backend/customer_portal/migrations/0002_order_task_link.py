import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customer_portal", "0001_initial"),
        ("tasks", "0003_alter_tasksteplog_action"),
    ]

    operations = [
        migrations.RemoveField(model_name="customerorder", name="staff_note"),
        migrations.RemoveField(model_name="customerorder", name="handled_by"),
        migrations.AddField(
            model_name="customerorder",
            name="task",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="customer_orders", to="tasks.task", verbose_name="تسک اصلی"),
        ),
        migrations.AlterField(
            model_name="customerorder",
            name="status",
            field=models.CharField(choices=[("pending", "در انتظار تأیید انباردار"), ("confirmed", "تأیید شد"), ("partial", "تأیید جزئی"), ("rejected", "تأمین نشد")], default="pending", max_length=20, verbose_name="وضعیت"),
        ),
    ]
