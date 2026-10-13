# purchasing/urls.py

from django.urls import path, include


urlpatterns = [
    path(
        "",
        include("quality_control.api.v1.quality_control.urls"),
    ),
    path(
        "employee/",
        include("quality_control.api.v1.employee.urls"),
    )
]