from django.urls import path

from .view import (
    MySignerListApi,
    PublicSignerDetailApi,
    PublicSignerSignApi,
    SignerCreateApi,
    SignerDeleteApi,
    SignerSignApi,
    SignerUpdateApi,
)

urlpatterns = [

    path(
        "public/<uuid:token>/",
        PublicSignerDetailApi.as_view(),
        name="signer-public-detail",
    ),

    path(
        "public/<uuid:token>/sign/",
        PublicSignerSignApi.as_view(),
        name="signer-public-sign",
    ),

    path(
        "my/",
        MySignerListApi.as_view(),
        name="signer-my-list",
    ),

    path(
        "create/",
        SignerCreateApi.as_view(),
        name="signer-create",
    ),

    path(
        "<int:pk>/update/",
        SignerUpdateApi.as_view(),
        name="signer-update",
    ),

    path(
        "<int:pk>/delete/",
        SignerDeleteApi.as_view(),
        name="signer-delete",
    ),

    path(
        "<int:pk>/sign/",
        SignerSignApi.as_view(),
        name="signer-sign",
    ),

]
