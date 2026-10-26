from django.urls import path

from .view import (
    DepartmentListApi,
    DepartmentChoiceListApi,
    DepartmentCreateApi,
    DepartmentDetailApi,
    DepartmentUpdateApi,
    DepartmentDeleteApi,
)


urlpatterns = [

    path(
        "list/",
        DepartmentListApi.as_view(),
        name="department-list",
    ),

    path(
        "choices/",
        DepartmentChoiceListApi.as_view(),
        name="department-choices",
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

]