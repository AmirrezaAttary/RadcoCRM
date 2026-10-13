from django.db import models

from .unit_measurement import (DimensionUnit, WeightUnit, VolumeUnit,
                                AreaUnit, CountUnit)

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class UNIT_TYPE(models.TextChoices):
    DIMENSION = "dimension", "ابعاد"
    WEIGHT = "weight", "وزن"
    VOLUME = "volume", "حجم"
    AREA = "area", "مساحت"
    COUNT = "count", "تعداد"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام کالا")
    sale_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت فروش")
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="دسته‌بندی"
    )

    
    unit_type = models.CharField(
        max_length=20,
        choices=UNIT_TYPE.choices,
        null=True,
        blank=True,
        verbose_name="نوع واحد"
    )

    dimension_unit = models.OneToOneField(
        DimensionUnit, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product",
        verbose_name="واحد ابعاد"
    )
    weight_unit = models.OneToOneField(
        WeightUnit, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product",
        verbose_name="واحد وزن"
    )
    volume_unit = models.OneToOneField(
        VolumeUnit, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product",
        verbose_name="واحد حجم"
    )
    area_unit = models.OneToOneField(
        AreaUnit, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product",
        verbose_name="واحد مساحت"
    )
    count_unit = models.OneToOneField(
        CountUnit, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product",
        verbose_name="واحد تعداد"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"

    def __str__(self):
        return self.name

    def get_unit(self):
        unit_map = {
            UNIT_TYPE.DIMENSION: self.dimension_unit,
            UNIT_TYPE.WEIGHT: self.weight_unit,
            UNIT_TYPE.VOLUME: self.volume_unit,
            UNIT_TYPE.AREA: self.area_unit,
            UNIT_TYPE.COUNT: self.count_unit,
        }
        return unit_map.get(self.unit_type)