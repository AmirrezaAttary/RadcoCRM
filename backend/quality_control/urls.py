# purchasing/urls.py

from django.urls import path, include


urlpatterns = [
    path(
        "api/v1/",
        include("quality_control.api.v1.urls"),
    )
]