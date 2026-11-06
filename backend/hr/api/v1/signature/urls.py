from django.urls import path

from .view import (
    MySignatureListApi,
    SignatureDetailApi,
    SignatureRegisterApi,
    SignatureSignApi,
)

urlpatterns = [

    path(
        "my/",
        MySignatureListApi.as_view(),
        name="hr-signature-my-list",
    ),

    path(
        "<int:pk>/",
        SignatureDetailApi.as_view(),
        name="hr-signature-detail",
    ),

    path(
        "<int:pk>/sign/",
        SignatureSignApi.as_view(),
        name="hr-signature-sign",
    ),

    path(
        "<int:pk>/register/",
        SignatureRegisterApi.as_view(),
        name="hr-signature-register",
    ),

]
