from django.urls import path

from access.api.v1.views.permission import (
    PermissionListApi,
)

from access.api.v1.views.employee_permission import (
    EmployeePermissionListCreateApi,
    EmployeePermissionDeleteApi,
)


app_name = "access"


urlpatterns = [
    path(
        "permissions/",
        PermissionListApi.as_view(),
        name="permission-list",
    ),

    path(
        "employees/<int:employee_id>/permissions/",
        EmployeePermissionListCreateApi.as_view(),
        name="employee-permission-list-create",
    ),

    path(
        "employees/<int:employee_id>/permissions/<path:permission_code>/",
        EmployeePermissionDeleteApi.as_view(),
        name="employee-permission-delete",
    ),
]