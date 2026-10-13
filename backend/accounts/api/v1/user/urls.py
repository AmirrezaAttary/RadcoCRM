from django.urls import path

from .view import (
    UserListApi,
    UserCreateApi,
    UserDetailApi,
    UserUpdateApi,
    UserDeleteApi,
)

urlpatterns = [
    path(
        "list/",
        UserListApi.as_view(),
        name="user-list",
    ),

    path(
        "create/",
        UserCreateApi.as_view(),
        name="user-create",
    ),

    path(
        "<int:pk>/",
        UserDetailApi.as_view(),
        name="user-detail",
    ),

    path(
        "<int:pk>/update/",
        UserUpdateApi.as_view(),
        name="user-update",
    ),

    path(
        "<int:pk>/delete/",
        UserDeleteApi.as_view(),
        name="user-delete",
    ),
]