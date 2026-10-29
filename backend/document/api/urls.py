from django.urls import include, path

urlpatterns = [
    path(
        "v1/",
        include("document.api.v1.urls"),
    ),
]