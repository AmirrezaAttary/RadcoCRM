from django.urls import path

from .views import (
    DocumentListCreateView,
    DocumentDetailView,
    DocumentFileListCreateView,
    DocumentFileDetailView,
    DocumentStepListCreateView,
    DocumentStepDetailView,
)


urlpatterns = [

    path(
        "",
        DocumentListCreateView.as_view(),
        name="document-list-create",
    ),

    path(
        "<int:pk>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),

    path(
        "<int:document_id>/files/",
        DocumentFileListCreateView.as_view(),
        name="document-file-list-create",
    ),

    path(
        "files/<int:pk>/",
        DocumentFileDetailView.as_view(),
        name="document-file-detail",
    ),

    path(
        "<int:document_id>/steps/",
        DocumentStepListCreateView.as_view(),
        name="document-step-list-create",
    ),

    path(
        "steps/<int:pk>/",
        DocumentStepDetailView.as_view(),
        name="document-step-detail",
    ),
]