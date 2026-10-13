from django.urls import path

from .views import (
    ProfileListView,
    ProfileDetailView,
    ProfileUpdateView,
    ProfilePatchView,
)


urlpatterns = [
    path(
        "profiles/",
        ProfileListView.as_view(),
        name="profile-list",
    ),

    path(
        "profiles/<int:pk>/",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),

    path(
        "profiles/<int:pk>/update/",
        ProfileUpdateView.as_view(),
        name="profile-update",
    ),

    path(
        "profiles/<int:pk>/patch/",
        ProfilePatchView.as_view(),
        name="profile-patch",
    ),
]