from django.urls import path

from .views import (
    PurchaseTaskAttachmentListView,
    PurchaseTaskAttachmentCreateView,
    PurchaseTaskAttachmentDetailView,
    PurchaseTaskAttachmentUpdateView,
    PurchaseTaskAttachmentPartialUpdateView,
    PurchaseTaskAttachmentDeleteView,
)


urlpatterns = [
    path(
        "",
        PurchaseTaskAttachmentListView.as_view(),
        name="purchase-task-attachment-list",
    ),

    path(
        "create/",
        PurchaseTaskAttachmentCreateView.as_view(),
        name="purchase-task-attachment-create",
    ),

    path(
        "<int:pk>/",
        PurchaseTaskAttachmentDetailView.as_view(),
        name="purchase-task-attachment-detail",
    ),

    path(
        "<int:pk>/update/",
        PurchaseTaskAttachmentUpdateView.as_view(),
        name="purchase-task-attachment-update",
    ),

    path(
        "<int:pk>/patch/",
        PurchaseTaskAttachmentPartialUpdateView.as_view(),
        name="purchase-task-attachment-partial-update",
    ),

    path(
        "<int:pk>/delete/",
        PurchaseTaskAttachmentDeleteView.as_view(),
        name="purchase-task-attachment-delete",
    ),
]