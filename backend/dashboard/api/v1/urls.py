from django.urls import path

from .views import (
    CancelledByDepartmentView,
    CustomerSourcesView,
    OverviewView,
    SalesChartView,
    SummaryView,
    TopExpertsView,
)

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="dashboard-overview"),
    path("summary/", SummaryView.as_view(), name="dashboard-summary"),
    path("sales-chart/", SalesChartView.as_view(), name="dashboard-sales-chart"),
    path("customer-sources/", CustomerSourcesView.as_view(), name="dashboard-customer-sources"),
    path("cancelled-by-department/", CancelledByDepartmentView.as_view(), name="dashboard-cancelled-by-department"),
    path("top-experts/", TopExpertsView.as_view(), name="dashboard-top-experts"),
]
