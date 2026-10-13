from django.urls import path

from .view import (
    DepartmentListApi,
    DepartmentCreateApi,
    DepartmentDetailApi,
    DepartmentUpdateApi,
    DepartmentDeleteApi,
    DepartmentActivateApi,
    DepartmentDeactivateApi,
)


urlpatterns = [

    path(
        "list/",
        DepartmentListApi.as_view(),
        name="department-list",
    ),

    path(
        "create/",
        DepartmentCreateApi.as_view(),
        name="department-create",
    ),

    path(
        "<int:pk>/",
        DepartmentDetailApi.as_view(),
        name="department-detail",
    ),

    path(
        "<int:pk>/update/",
        DepartmentUpdateApi.as_view(),
        name="department-update",
    ),

    path(
        "<int:pk>/delete/",
        DepartmentDeleteApi.as_view(),
        name="department-delete",
    ),

    path(
        "<int:pk>/activate/",
        DepartmentActivateApi.as_view(),
        name="department-activate",
    ),

    path(
        "<int:pk>/deactivate/",
        DepartmentDeactivateApi.as_view(),
        name="department-deactivate",
    ),

]