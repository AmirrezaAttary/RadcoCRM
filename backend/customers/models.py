from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Customer(models.Model):

    class CustomerStatus(models.IntegerChoices):
        POTENTIAL = 1, "مشتری بالقوه"
        ACTIVE = 2, "مشتری بالفعل"

    full_name = models.CharField(max_length=255, verbose_name="نام و نام خانوادگی")
    job_title = models.CharField(max_length=255, blank=True, verbose_name="سمت شغلی")
    phone_number = models.CharField(max_length=20, verbose_name="شماره تماس")
    company_name = models.CharField(max_length=255, blank=True, verbose_name="نام شرکت")
    address = models.TextField(blank=True, verbose_name="آدرس")
    source = models.CharField(max_length=255, blank=True, verbose_name="منبع آشنایی")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    status = models.IntegerField(
        choices=CustomerStatus.choices,
        default=CustomerStatus.POTENTIAL,
        verbose_name="وضعیت مشتری",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_customers",
        verbose_name="ثبت‌کننده",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name
    

class CustomerScore(models.Model):

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name="مشتری",
    )

    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.PROTECT,
        related_name="customer_scores",
        verbose_name="کارمند",
    )

    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        verbose_name="امتیاز",
    )

    reason = models.TextField(
        verbose_name="دلیل امتیاز",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    class Meta:
        verbose_name = "امتیاز مشتری"
        verbose_name_plural = "امتیازات مشتریان"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.full_name} - {self.score}"