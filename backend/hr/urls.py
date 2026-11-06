from django.urls import include, path

urlpatterns = [
    path(
        "api/v1/",
        include("hr.api.v1.urls"),
    ),
]
