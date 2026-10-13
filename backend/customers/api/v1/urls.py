from django.urls import path

from .views import (
    CustomerListApi,
    CustomerCreateApi,
    CustomerDetailApi,
    CustomerUpdateApi,
    CustomerDeleteApi,
    CustomerActivateApi,
    CustomerDeactivateApi,
    CustomerScoreListCreateView,
    CustomerScoreDetailView,
)

app_name = "customers"

urlpatterns = [
    path("customers/", CustomerListApi.as_view(), name="customer-list"),
    path("customers/create/", CustomerCreateApi.as_view(), name="customer-create"),
    path("customers/<int:pk>/", CustomerDetailApi.as_view(), name="customer-detail"),
    path("customers/<int:pk>/update/", CustomerUpdateApi.as_view(), name="customer-update"),
    path("customers/<int:pk>/delete/", CustomerDeleteApi.as_view(), name="customer-delete"),
    path(
        "customers/<int:customer_id>/scores/",
        CustomerScoreListCreateView.as_view(),
        name="customer-score-list-create",
    ),

    path(
        "customers/<int:customer_id>/scores/<int:pk>/",
        CustomerScoreDetailView.as_view(),
        name="customer-score-detail",
    ),
    
    path(
        "customers/<int:pk>/activate/",
        CustomerActivateApi.as_view(),
        name="customer-activate",
    ),

    path(
        "customers/<int:pk>/deactivate/",
        CustomerDeactivateApi.as_view(),
        name="customer-deactivate",
    ),
]