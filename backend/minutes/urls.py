from django.urls import include, path

urlpatterns = [
    path(
        "api/v1/",
        include("minutes.api.v1.urls"),
    ),
]
