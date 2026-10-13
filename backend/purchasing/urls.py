# purchasing/urls.py

from django.urls import path, include


urlpatterns = [
    path(
        "api/v1/",
        include("purchasing.api.v1.urls"),
    )
]