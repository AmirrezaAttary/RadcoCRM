from django.urls import include, path

urlpatterns = [
    path("api/", include("absence.api.v1.urls")),
]