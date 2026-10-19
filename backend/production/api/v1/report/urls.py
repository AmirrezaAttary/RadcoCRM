from django.urls import path

from .views import MonthlyProductionReportView


urlpatterns = [
    path(
        "monthly/",
        MonthlyProductionReportView.as_view(),
        name="production-report-monthly",
    ),
]
