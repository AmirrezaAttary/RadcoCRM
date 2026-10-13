from django.urls import include, path

urlpatterns = [
    path(
        "api/v1/",
        include("department.api.v1.urls"),
    ),
]