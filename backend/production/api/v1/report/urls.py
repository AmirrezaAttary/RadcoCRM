from django.urls import path

from .views import (
    MachineMonthlyReportView,
    MachineSummaryReportView,
    MonthlyProductionReportView,
)


urlpatterns = [
    path(
        "monthly/",
        MonthlyProductionReportView.as_view(),
        name="production-report-monthly",
    ),
    path(
        "machine/summary/",
        MachineSummaryReportView.as_view(),
        name="production-report-machine-summary",
    ),
    path(
        "machine/monthly/",
        MachineMonthlyReportView.as_view(),
        name="production-report-machine-monthly",
    ),
]
