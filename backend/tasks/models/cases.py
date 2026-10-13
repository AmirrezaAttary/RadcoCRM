from django.conf import settings
from django.db import models


class Resource(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان منبع",
    )

    class Meta:
        verbose_name = "منبع"
        verbose_name_plural = "منابع"
        ordering = ["title"]

    def __str__(self):
        return self.title

class Case(models.Model):

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="cases",
        verbose_name="مشتری",
    )

    title = models.CharField(max_length=255, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    resources = models.ManyToManyField(
        Resource,
        related_name="cases",
        blank=True,
        verbose_name="منابع",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_cases",
        verbose_name="ایجادکننده",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پرونده"
        verbose_name_plural = "پرونده‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
