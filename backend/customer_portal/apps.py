from django.apps import AppConfig


class CustomerPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customer_portal"
    verbose_name = "پرتال مشتریان"

    def ready(self):
        from . import signals  # noqa: F401
