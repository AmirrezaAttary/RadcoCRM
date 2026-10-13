from django.urls import path

from .views import (
    PurchaseProcessEmployeeListView,
    PurchaseProcessEmployeeDetailView,
    PurchaseProcessEmployeeUpdateView,
    PurchaseProcessEmployeePartialUpdateView,
    PurchaseProcessEmployeeDeleteView,
    PurchaseProcessEmployeeCreateView,
)


urlpatterns = [
    path(
        "",
        PurchaseProcessEmployeeListView.as_view(),
        name="purchase-process-employee-list",
    ),
    path(
        "create/",
        PurchaseProcessEmployeeCreateView.as_view(),
        name="purchase-process-employee-create",
    ),
    path(
        "<int:pk>/",
        PurchaseProcessEmployeeDetailView.as_view(),
        name="purchase-process-employee-detail",
    ),
    path(
        "<int:pk>/update/",
        PurchaseProcessEmployeeUpdateView.as_view(),
        name="purchase-process-employee-update",
    ),
    path(
        "<int:pk>/patch/",
        PurchaseProcessEmployeePartialUpdateView.as_view(),
        name="purchase-process-employee-partial-update",
    ),
    path(
        "<int:pk>/delete/",
        PurchaseProcessEmployeeDeleteView.as_view(),
        name="purchase-process-employee-delete",
    ),
]