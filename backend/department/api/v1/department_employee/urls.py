from django.urls import path

from .view import (
    DepartmentEmployeeActivateApi,
    DepartmentEmployeeCreateApi,
    DepartmentEmployeeDeactivateApi,
    DepartmentEmployeeDeleteApi,
    DepartmentEmployeeDetailApi,
    DepartmentEmployeeListApi,
    DepartmentEmployeeUpdateApi,
)

urlpatterns = [

    path(
        "list/",
        DepartmentEmployeeListApi.as_view(),
        name="department-employee-list",
    ),

    path(
        "create/",
        DepartmentEmployeeCreateApi.as_view(),
        name="department-employee-create",
    ),

    path(
        "<int:pk>/",
        DepartmentEmployeeDetailApi.as_view(),
        name="department-employee-detail",
    ),

    path(
        "<int:pk>/update/",
        DepartmentEmployeeUpdateApi.as_view(),
        name="department-employee-update",
    ),

    path(
        "<int:pk>/delete/",
        DepartmentEmployeeDeleteApi.as_view(),
        name="department-employee-delete",
    ),
    
    path(
        "<int:department_id>/<int:employee_id>/deactivate/",
        DepartmentEmployeeDeactivateApi.as_view(),
        name="department-employee-deactivate",
    ),

    path(
        "<int:department_id>/<int:employee_id>/activate/",
        DepartmentEmployeeActivateApi.as_view(),
        name="department-employee-activate",
    ),

]