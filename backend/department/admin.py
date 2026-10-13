from django.contrib import admin

from .models.department import Department
from .models.department_employee import DepartmentEmployee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


@admin.register(DepartmentEmployee)
class DepartmentEmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "department",
        "created_at",
    )

    list_filter = (
        "department",
    )

    search_fields = (
        "employee__full_name",
        "department__name",
    )

    autocomplete_fields = (
        "employee",
        "department",
    )