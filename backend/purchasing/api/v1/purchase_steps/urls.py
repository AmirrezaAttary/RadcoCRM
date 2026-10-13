from django.urls import path

from .views import (
    PurchaseProcessStepListView,
    PurchaseProcessStepCreateView,
    PurchaseProcessStepDetailView,
    PurchaseProcessStepUpdateView,
    PurchaseProcessStepPartialUpdateView,
    PurchaseProcessStepDeleteView,
)


urlpatterns = [
    path(
        "",
        PurchaseProcessStepListView.as_view(),
        name="purchase-process-step-list",
    ),
    path(
        "create/",
        PurchaseProcessStepCreateView.as_view(),
        name="purchase-process-step-create",
    ),
    path(
        "<int:pk>/",
        PurchaseProcessStepDetailView.as_view(),
        name="purchase-process-step-detail",
    ),
    path(
        "<int:pk>/update/",
        PurchaseProcessStepUpdateView.as_view(),
        name="purchase-process-step-update",
    ),
    path(
        "<int:pk>/patch/",
        PurchaseProcessStepPartialUpdateView.as_view(),
        name="purchase-process-step-partial-update",
    ),
    path(
        "<int:pk>/delete/",
        PurchaseProcessStepDeleteView.as_view(),
        name="purchase-process-step-delete",
    ),
]