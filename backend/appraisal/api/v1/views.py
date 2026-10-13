# appraisal/api/v1/views.py

from datetime import datetime, time, timedelta

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from appraisal.services.calendar import CalendarService

from .serializers import (
    CalendarEventSerializer,
    CalendarResponseSerializer,
)


class CalendarView(generics.GenericAPIView):
    serializer_class = CalendarEventSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="start",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="تاریخ شروع بازه تقویم",
            ),
            OpenApiParameter(
                name="end",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="تاریخ پایان بازه تقویم",
            ),
        ],
        responses={
            200: CalendarResponseSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if not start or not end:
            return Response(
                {
                    "detail": "پارامترهای start و end الزامی هستند."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(
                start,
                "%Y-%m-%d",
            ).date()

            end_date = datetime.strptime(
                end,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            return Response(
                {
                    "detail": (
                        "فرمت start و end باید به صورت "
                        "YYYY-MM-DD باشد."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date > end_date:
            return Response(
                {
                    "detail": "start نمی‌تواند بعد از end باشد."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_datetime = timezone.make_aware(
            datetime.combine(
                start_date,
                time.min,
            )
        )

        # end is exclusive
        end_datetime = (
            timezone.make_aware(
                datetime.combine(
                    end_date,
                    time.min,
                )
            )
            + timedelta(days=1)
        )

        events = CalendarService.get_events(
            user=request.user,
            start=start_datetime,
            end=end_datetime,
        )

        event_serializer = self.get_serializer(
            events,
            many=True,
        )

        response_data = {
            "start": start,
            "end": end,
            "events": event_serializer.data,
        }

        return Response(response_data)