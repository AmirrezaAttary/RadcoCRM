from django.contrib import admin

from .models.user import User
from .models.employee import Employee


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "type",
        "is_active",
        "created_at",
    )

    list_filter = (
        "type",
        "is_active",
    )

    search_fields = (
        "username",
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "created_at",
    )

    search_fields = (
        "user__username",
    )