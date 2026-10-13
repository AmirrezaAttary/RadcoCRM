# appraisal/urls.py

from django.urls import path, include


urlpatterns = [
    path(
        "api/v1/",
        include("search.api.v1.urls"),
    )
]