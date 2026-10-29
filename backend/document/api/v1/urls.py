from django.urls import path

from .views import (
    DocumentListCreateView,
    DocumentDetailView,
    DocumentFileListCreateView,
    DocumentFileDetailView,
    DocumentStepListCreateView,
    DocumentStepDetailView,
    DocumentStepFileListCreateView,
    DocumentStepFilePutView,
    DocumentStepFilePatchView,
    DocumentStepFileDeleteView,
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

    path(
        "<int:document_id>/steps/<int:step_id>/files/",
        DocumentStepFileListCreateView.as_view(),
        name="document-step-file-list-create",
    ),

    path(
        "<int:document_id>/steps/<int:step_id>/files/<int:file_id>/put/",
        DocumentStepFilePutView.as_view(),
        name="document-step-file-put",
    ),

    path(
        "<int:document_id>/steps/<int:step_id>/files/<int:file_id>/patch/",
        DocumentStepFilePatchView.as_view(),
        name="document-step-file-patch",
    ),

    path(
        "<int:document_id>/steps/<int:step_id>/files/<int:file_id>/delete/",
        DocumentStepFileDeleteView.as_view(),
        name="document-step-file-delete",
    ),
]