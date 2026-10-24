from django.urls import path

from .views import CaseReportApi

app_name = "case_report"

urlpatterns = [
    path(
        "<int:pk>/report/",
        CaseReportApi.as_view(),
        name="case-report",
    ),
]
