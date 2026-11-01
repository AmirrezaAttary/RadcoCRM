from django.urls import path

from .view import (
    LoginApi,
    MeApi,
    MeAvatarApi,
    RefreshTokenApi,
)



urlpatterns = [

    path(
        "login/",
        LoginApi.as_view(),
        name="login",
    ),
    path(
        "me/",
        MeApi.as_view(),
        name="me",
    ),
    path(
        "me/avatar/",
        MeAvatarApi.as_view(),
        name="me-avatar",
    ),
    path(
        "refresh/",
        RefreshTokenApi.as_view(),
        name="refresh",
    ),

]