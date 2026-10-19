
from django.apps import apps
from django.contrib import admin
from django.db import models


class AutoModelAdmin(admin.ModelAdmin):
    """تنظیمات عمومی برای نمایش مدل‌های برنامه در پنل مدیریت."""

    def get_list_display(self, request):
        fields = [
            field.name for field in self.model._meta.concrete_fields
            if not getattr(field, "many_to_many", False)
        ]
        return tuple(fields[:8]) or ("__str__",)

    def get_search_fields(self, request):
        fields = [
            field.name for field in self.model._meta.concrete_fields
            if isinstance(field, (models.CharField, models.TextField, models.EmailField))
        ]
        return tuple(fields[:8])

    def get_list_filter(self, request):
        fields = []
        for field in self.model._meta.concrete_fields:
            if getattr(field, "choices", None) or isinstance(
                field, (models.BooleanField, models.ForeignKey, models.OneToOneField)
            ):
                fields.append(field.name)
        return tuple(fields[:6])

    def get_readonly_fields(self, request, obj=None):
        return tuple(
            field.name for field in self.model._meta.concrete_fields
            if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False)
        )


_APP_LABEL = __name__.split(".")[0]
_APP_CONFIG = apps.get_app_config(_APP_LABEL)

for _model in _APP_CONFIG.get_models():
    if _model not in admin.site._registry:
        admin.site.register(_model, AutoModelAdmin)
