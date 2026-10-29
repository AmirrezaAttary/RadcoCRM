from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class CustomerPortalAccount(models.Model):
    """
    حساب ورود مشتری به پرتال سفارش.

    - customer   : مشتری‌ای که این حساب برای اوست (هر مشتری حداکثر یک حساب)
    - granted_by : کاربری (ادمین) که دسترسی را صادر کرده
    - password   : هش‌شده ذخیره می‌شود (هرگز متن خام)

    عمداً User جدید ساخته نمی‌شود تا توکن مشتری هیچ‌وقت به APIهای
    داخلی (که با IsAuthenticated باز هستند) دسترسی پیدا نکند.
    """

    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="portal_account",
        verbose_name="مشتری",
    )

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="granted_portal_accounts",
        verbose_name="صادرکننده دسترسی",
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name="نام کاربری",
    )

    password = models.CharField(
        max_length=128,
        verbose_name="رمز عبور (هش‌شده)",
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین ورود",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "حساب پرتال مشتری"
        verbose_name_plural = "حساب‌های پرتال مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.customer.full_name})"

    # --- سازگاری با DRF (request.user) ---
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # --- رمز عبور ---
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class CustomerOrder(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        CONFIRMED = "confirmed", "تأیید شد"
        REJECTED = "rejected", "رد شد"
        CANCELLED = "cancelled", "لغو توسط مشتری"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="portal_orders",
        verbose_name="مشتری",
    )

    account = models.ForeignKey(
        CustomerPortalAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="حساب ثبت‌کننده",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    note = models.TextField(blank=True, verbose_name="توضیحات مشتری")

    staff_note = models.TextField(blank=True, verbose_name="توضیحات کارمند")

    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_customer_orders",
        verbose_name="بررسی‌کننده",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سفارش مشتری"
        verbose_name_plural = "سفارش‌های مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return f"سفارش #{self.pk} - {self.customer.full_name}"


class CustomerOrderItem(models.Model):

    order = models.ForeignKey(
        CustomerOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    product = models.ForeignKey(
        "warehouse.Product",
        on_delete=models.PROTECT,
        related_name="customer_order_items",
        verbose_name="کالا",
    )

    quantity = models.FloatField(verbose_name="تعداد")

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="قیمت واحد در زمان ثبت",
    )

    class Meta:
        verbose_name = "آیتم سفارش مشتری"
        verbose_name_plural = "آیتم‌های سفارش مشتری"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_customer_order_product",
            ),
        ]

    def __str__(self):
        return f"{self.order_id} | {self.product.name} | {self.quantity}"
