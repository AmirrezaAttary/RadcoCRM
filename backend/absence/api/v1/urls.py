from django.urls import include, path

urlpatterns = [
    path("v1/", include("absence.api.v1.absence.urls")),
]