from django.urls import path

from .view import (
    AbsenceListView,
    AbsenceCreateView,
    AbsenceRetrieveView,
    AbsenceUpdateView,
    AbsencePatchView,
    AbsenceDeleteView,
    AbsenceApproveView,
    AbsenceRejectView,
    AbsenceAttachmentListView,
    AbsenceAttachmentCreateView,
    AbsenceAttachmentRetrieveView,
    AbsenceAttachmentUpdateView,
    AbsenceAttachmentPatchView,
    AbsenceAttachmentDeleteView,
)


urlpatterns = [

    path(
        "",
        AbsenceListView.as_view(),
        name="absence-list",
    ),

    path(
        "create/",
        AbsenceCreateView.as_view(),
        name="absence-create",
    ),

    path(
        "<int:pk>/",
        AbsenceRetrieveView.as_view(),
        name="absence-retrieve",
    ),

    path(
        "<int:pk>/update/",
        AbsenceUpdateView.as_view(),
        name="absence-update",
    ),

    path(
        "<int:pk>/patch/",
        AbsencePatchView.as_view(),
        name="absence-patch",
    ),

    path(
        "<int:pk>/delete/",
        AbsenceDeleteView.as_view(),
        name="absence-delete",
    ),

    path(
        "<int:pk>/approve/",
        AbsenceApproveView.as_view(),
        name="absence-approve",
    ),

    path(
        "<int:pk>/reject/",
        AbsenceRejectView.as_view(),
        name="absence-reject",
    ),

    path(
        "<int:absence_id>/attachment/",
        AbsenceAttachmentListView.as_view(),
        name="absence-attachment-list",
    ),

    path(
        "<int:absence_id>/attachment/create/",
        AbsenceAttachmentCreateView.as_view(),
        name="absence-attachment-create",
    ),

    path(
        "<int:absence_id>/attachment/<int:pk>/",
        AbsenceAttachmentRetrieveView.as_view(),
        name="absence-attachment-retrieve",
    ),

    path(
        "<int:absence_id>/attachment/<int:pk>/update/",
        AbsenceAttachmentUpdateView.as_view(),
        name="absence-attachment-update",
    ),

    path(
        "<int:absence_id>/attachment/<int:pk>/patch/",
        AbsenceAttachmentPatchView.as_view(),
        name="absence-attachment-patch",
    ),

    path(
        "<int:absence_id>/attachment/<int:pk>/delete/",
        AbsenceAttachmentDeleteView.as_view(),
        name="absence-attachment-delete",
    ),
]