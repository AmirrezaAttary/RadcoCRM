from django.urls import path

from .view import (
    ContractCancelApi,
    ContractCreateApi,
    ContractDeleteApi,
    ContractDetailApi,
    ContractListApi,
    ContractSendApi,
    ContractUpdateApi,
)

urlpatterns = [

    path("list/", ContractListApi.as_view(), name="hr-contract-list"),

    path("create/", ContractCreateApi.as_view(), name="hr-contract-create"),

    path("<int:pk>/", ContractDetailApi.as_view(), name="hr-contract-detail"),

    path("<int:pk>/update/", ContractUpdateApi.as_view(), name="hr-contract-update"),

    path("<int:pk>/delete/", ContractDeleteApi.as_view(), name="hr-contract-delete"),

    path("<int:pk>/send/", ContractSendApi.as_view(), name="hr-contract-send"),

    path("<int:pk>/cancel/", ContractCancelApi.as_view(), name="hr-contract-cancel"),

]
