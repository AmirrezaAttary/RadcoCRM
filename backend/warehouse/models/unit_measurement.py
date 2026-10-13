from django.db import models


class DimensionUnit(models.Model):
    meter = models.FloatField(null=True, blank=True, verbose_name="متر")
    centimeter = models.FloatField(null=True, blank=True, verbose_name="سانتیمتر")
    inch = models.FloatField(null=True, blank=True, verbose_name="اینچ")

    class Meta:
        verbose_name = "واحد ابعاد"
        verbose_name_plural = "واحدهای ابعاد"


class WeightUnit(models.Model):

    gram = models.FloatField(null=True, blank=True, verbose_name="گرم")
    kilogram = models.FloatField(null=True, blank=True, verbose_name="کیلوگرم")
    milligram = models.FloatField(null=True, blank=True, verbose_name="میلی‌گرم")
    ton = models.FloatField(null=True, blank=True, verbose_name="تن")

    class Meta:
        verbose_name = "واحد وزن"
        verbose_name_plural = "واحدهای وزن"


class VolumeUnit(models.Model):

    liter = models.FloatField(null=True, blank=True, verbose_name="لیتر")
    milliliter = models.FloatField(null=True, blank=True, verbose_name="میلی‌لیتر")
    gallon = models.FloatField(null=True, blank=True, verbose_name="گالن")

    class Meta:
        verbose_name = "واحد حجم"
        verbose_name_plural = "واحدهای حجم"


class AreaUnit(models.Model):

    square_meter = models.FloatField(null=True, blank=True, verbose_name="متر مربع")
    square_centimeter = models.FloatField(null=True, blank=True, verbose_name="سانتیمتر مربع")

    class Meta:
        verbose_name = "واحد مساحت"
        verbose_name_plural = "واحدهای مساحت"


class CountUnit(models.Model):
    quantity_per_unit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="تعداد در هر بسته",
    )

    class Meta:
        verbose_name = "واحد تعداد"
        verbose_name_plural = "واحدهای تعداد"

    def __str__(self):
        return f"{self.quantity_per_unit} عدد"
