from django.urls import path

from .view import (
    EmployeeCreateApi,
    EmployeeDeleteApi,
    EmployeeDetailApi,
    EmployeeListApi,
    EmployeeUpdateApi,
)

urlpatterns = [

    path(
        "list/",
        EmployeeListApi.as_view(),
        name="employee-list",
    ),

    path(
        "create/",
        EmployeeCreateApi.as_view(),
        name="employee-create",
    ),

    path(
        "<int:pk>/",
        EmployeeDetailApi.as_view(),
        name="employee-detail",
    ),

    path(
        "<int:pk>/update/",
        EmployeeUpdateApi.as_view(),
        name="employee-update",
    ),

    path(
        "<int:pk>/delete/",
        EmployeeDeleteApi.as_view(),
        name="employee-delete",
    ),

]