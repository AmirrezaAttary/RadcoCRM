# appraisal/api/v1/urls.py

from django.urls import path

from .views import CalendarView


urlpatterns = [
    path(
        "calendar/",
        CalendarView.as_view(),
        name="calendar",
    ),
]