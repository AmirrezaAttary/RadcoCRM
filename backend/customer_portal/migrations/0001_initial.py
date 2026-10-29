from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customers", "0001_initial"),
        ("warehouse", "0007_product_shelf_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerPortalAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="نام کاربری")),
                ("password", models.CharField(max_length=128, verbose_name="رمز عبور (هش\u200cشده)")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="آخرین ورود")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="portal_account", to="customers.customer", verbose_name="مشتری")),
                ("granted_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="granted_portal_accounts", to=settings.AUTH_USER_MODEL, verbose_name="صادرکننده دسترسی")),
            ],
            options={
                "verbose_name": "حساب پرتال مشتری",
                "verbose_name_plural": "حساب\u200cهای پرتال مشتریان",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CustomerOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("confirmed", "تأیید شد"), ("rejected", "رد شد"), ("cancelled", "لغو توسط مشتری")], default="pending", max_length=20, verbose_name="وضعیت")),
                ("note", models.TextField(blank=True, verbose_name="توضیحات مشتری")),
                ("staff_note", models.TextField(blank=True, verbose_name="توضیحات کارمند")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="customer_portal.customerportalaccount", verbose_name="حساب ثبت\u200cکننده")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="portal_orders", to="customers.customer", verbose_name="مشتری")),
                ("handled_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="handled_customer_orders", to=settings.AUTH_USER_MODEL, verbose_name="بررسی\u200cکننده")),
            ],
            options={
                "verbose_name": "سفارش مشتری",
                "verbose_name_plural": "سفارش\u200cهای مشتریان",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CustomerOrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.FloatField(verbose_name="تعداد")),
                ("unit_price", models.DecimalField(decimal_places=0, max_digits=12, verbose_name="قیمت واحد در زمان ثبت")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="customer_portal.customerorder", verbose_name="سفارش")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="customer_order_items", to="warehouse.product", verbose_name="کالا")),
            ],
            options={
                "verbose_name": "آیتم سفارش مشتری",
                "verbose_name_plural": "آیتم\u200cهای سفارش مشتری",
                "ordering": ["id"],
            },
        ),
        migrations.AddConstraint(
            model_name="customerorderitem",
            constraint=models.UniqueConstraint(fields=("order", "product"), name="unique_customer_order_product"),
        ),
    ]
