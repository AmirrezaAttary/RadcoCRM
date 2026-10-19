from django.urls import path, include


urlpatterns = [
    path(
        "machine/",
        include("production.api.v1.machine.urls"),
    ),
    path(
        "log/",
        include("production.api.v1.production_log.urls"),
    ),
    path(
        "report/",
        include("production.api.v1.report.urls"),
    ),
]
