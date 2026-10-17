from django.urls import path

from .view import (
    MeetingCancelApi,
    MeetingCreateApi,
    MeetingDeleteApi,
    MeetingDetailApi,
    MeetingListApi,
    MeetingSendApi,
    MeetingUpdateApi,
)

urlpatterns = [

    path(
        "list/",
        MeetingListApi.as_view(),
        name="meeting-list",
    ),

    path(
        "create/",
        MeetingCreateApi.as_view(),
        name="meeting-create",
    ),

    path(
        "<int:pk>/",
        MeetingDetailApi.as_view(),
        name="meeting-detail",
    ),

    path(
        "<int:pk>/update/",
        MeetingUpdateApi.as_view(),
        name="meeting-update",
    ),

    path(
        "<int:pk>/delete/",
        MeetingDeleteApi.as_view(),
        name="meeting-delete",
    ),

    path(
        "<int:pk>/send/",
        MeetingSendApi.as_view(),
        name="meeting-send",
    ),

    path(
        "<int:pk>/cancel/",
        MeetingCancelApi.as_view(),
        name="meeting-cancel",
    ),

]
