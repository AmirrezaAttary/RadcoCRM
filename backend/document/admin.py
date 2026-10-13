from django.apps import apps
from django.contrib import admin
from django.db import models


class AutoModelAdmin(admin.ModelAdmin):
    """Useful default admin configuration for models in this app."""

    def get_list_display(self, request):
        fields = []
        for field in self.model._meta.get_fields():
            if getattr(field, "concrete", False) and not getattr(field, "many_to_many", False):
                fields.append(field.name)
        return tuple(fields[:8]) or ("__str__",)

    def get_search_fields(self, request):
        fields = []
        for field in self.model._meta.get_fields():
            if not getattr(field, "concrete", False):
                continue
            if isinstance(field, (models.CharField, models.TextField, models.EmailField)):
                fields.append(field.name)
        return tuple(fields[:8])

    def get_list_filter(self, request):
        filters = []
        for field in self.model._meta.get_fields():
            if not getattr(field, "concrete", False):
                continue
            if getattr(field, "choices", None) or isinstance(field, (models.BooleanField, models.ForeignKey, models.OneToOneField)):
                filters.append(field.name)
        return tuple(filters[:6])

    def get_readonly_fields(self, request, obj=None):
        return tuple(
            field.name
            for field in self.model._meta.get_fields()
            if getattr(field, "concrete", False) and getattr(field, "auto_now", False)
        )


_app_label = __name__.split(".")[0]
_app_config = apps.get_app_config(_app_label)

for _model in _app_config.get_models():
    if _model not in admin.site._registry:
        admin.site.register(_model, AutoModelAdmin)
