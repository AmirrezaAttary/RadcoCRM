from django.urls import include, path

urlpatterns = [
    path(
        "meeting/",
        include("minutes.api.v1.meeting.urls"),
    ),

    path(
        "signer/",
        include("minutes.api.v1.signer.urls"),
    ),
]
