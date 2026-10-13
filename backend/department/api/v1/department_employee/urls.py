from django.urls import path

from .view import (
    DepartmentEmployeeCreateApi,
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

]