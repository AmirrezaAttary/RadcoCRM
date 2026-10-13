from django.urls import include, path

urlpatterns = [
    path(
        "api/v1/",
        include("accounts.api.v1.urls"),
    ),
]