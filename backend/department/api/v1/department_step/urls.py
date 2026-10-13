from django.urls import path

from .view import (
    DepartmentStepListApi,
    DepartmentStepCreateApi,
    DepartmentStepDetailApi,
    DepartmentStepUpdateApi,
    DepartmentStepDeleteApi,
    DepartmentStepActivateApi,
    DepartmentStepDeactivateApi,
)


urlpatterns = [
    path(
        "",
        DepartmentStepListApi.as_view(),
        name="list",
    ),
    path(
        "create/",
        DepartmentStepCreateApi.as_view(),
        name="create",
    ),
    path(
        "<int:pk>/",
        DepartmentStepDetailApi.as_view(),
        name="detail",
    ),
    path(
        "<int:pk>/update/",
        DepartmentStepUpdateApi.as_view(),
        name="update",
    ),
    path(
        "<int:pk>/delete/",
        DepartmentStepDeleteApi.as_view(),
        name="delete",
    ),
    path(
        "<int:pk>/activate/",
        DepartmentStepActivateApi.as_view(),
        name="activate",
    ),
    path(
        "<int:pk>/deactivate/",
        DepartmentStepDeactivateApi.as_view(),
        name="deactivate",
    ),
]