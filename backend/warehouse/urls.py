from django.urls import include, path

urlpatterns = [
    path(
        "api/v1/",
        include("warehouse.api.v1.urls"),
    ),
]