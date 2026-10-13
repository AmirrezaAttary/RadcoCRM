from datetime import datetime

from appraisal.services.providers import (
    TaskCalendarProvider,
    NoteCalendarProvider,
    OrderTaskCalendarProvider,
    InternalTaskRoutineCalendarProvider,
)
from appraisal.services.types import CalendarEvent


class CalendarService:

    providers = (
        TaskCalendarProvider,
        InternalTaskRoutineCalendarProvider,
        NoteCalendarProvider,
        OrderTaskCalendarProvider,
    )

    @classmethod
    def get_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> list[CalendarEvent]:

        events: list[CalendarEvent] = []

        for provider in cls.providers:
            events.extend(
                provider.get_events(
                    user=user,
                    start=start,
                    end=end,
                )
            )

        return events