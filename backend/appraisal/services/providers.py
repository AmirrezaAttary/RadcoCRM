from datetime import datetime, timedelta
from typing import List

from django.db.models import Q

from accounts.models import User
from appraisal.services.types import CalendarEvent, CalendarPerson
from access.internal_task import InternalTaskAccess
from note.models import Note
from tasks.models.internal_task import (
    InternalTaskDeadline,
    InternalTaskRoutine,
)
from tasks.models.tasks import TaskStepDeadline
from warehouse.models.warehouse_order_task import OrderTaskDeadline


def employee_to_calendar_person(employee) -> CalendarPerson:
    return CalendarPerson(
        id=employee.id,
        full_name=employee.full_name,
    )


def user_to_calendar_person(user) -> CalendarPerson:
    employee = getattr(user, "employee_profile", None)

    return CalendarPerson(
        id=user.id,
        full_name=(
            employee.full_name
            if employee is not None
            else user.username
        ),
    )


class TaskCalendarProvider:
    event_types = {
        "task": "task",
        "internal_task": "internal_task",
    }

    @classmethod
    def get_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        events = []

        events.extend(
            cls._get_task_events(
                user=user,
                start=start,
                end=end,
            )
        )

        events.extend(
            cls._get_internal_task_events(
                user=user,
                start=start,
                end=end,
            )
        )

        return events

    @classmethod
    def _get_task_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        deadlines = (
            TaskStepDeadline.objects
            .filter(
                Q(
                    started_at__gte=start,
                    started_at__lt=end,
                )
                |
                Q(
                    deadline__gte=start,
                    deadline__lt=end,
                )
            )
            .select_related(
                "task",
                "department_step",
            )
            .prefetch_related(
                "task__assigned_employee",
            )
        )

        if user.type != User.UserType.ADMIN:
            deadlines = deadlines.filter(
                Q(task__assigned_employee__user=user)
                |
                Q(task__created_by=user)
            ).distinct()

        return [
            CalendarEvent(
                id=deadline.task.id,
                title=(
                    f"{deadline.task.title} - "
                    f"{deadline.department_step.name}"
                ),
                start=deadline.started_at,
                end=deadline.deadline,
                type=cls.event_types["task"],
                people={
                    "assigned_employee": [
                        employee_to_calendar_person(employee)
                        for employee in deadline.task.assigned_employee.all()
                    ],
                    "created_by": user_to_calendar_person(
                        deadline.task.created_by
                    ),
                },
            )
            for deadline in deadlines
        ]

    @classmethod
    def _get_internal_task_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        deadlines = (
            InternalTaskDeadline.objects
            .filter(
                Q(
                    started_at__gte=start,
                    started_at__lt=end,
                )
                |
                Q(
                    deadline__gte=start,
                    deadline__lt=end,
                )
            )
            .select_related(
                "task",
                "task__created_by",
            )
            .prefetch_related(
                "task__assigned_to",
            )
        )

        if user.type != User.UserType.ADMIN:
            deadlines = deadlines.filter(
                Q(task__assigned_to=user)
                |
                Q(task__created_by=user)
            ).distinct()

        return [
            CalendarEvent(
                id=deadline.task.id,
                title=deadline.task.title,
                start=deadline.started_at,
                end=deadline.deadline,
                type=cls.event_types["internal_task"],
                people={
                    "assigned_to": [
                        user_to_calendar_person(assigned_user)
                        for assigned_user in deadline.task.assigned_to.all()
                    ],
                    "created_by": user_to_calendar_person(
                        deadline.task.created_by
                    ),
                },
            )
            for deadline in deadlines
        ]


class NoteCalendarProvider:
    event_type = "note"

    @classmethod
    def get_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        notes = (
            Note.objects
            .filter(user=user)
            .filter(
                Q(
                    created_at__gte=start,
                    created_at__lt=end,
                )
                |
                Q(
                    updated_at__gte=start,
                    updated_at__lt=end,
                )
            )
        )

        return [
            CalendarEvent(
                id=note.id,
                title=note.description,
                start=note.created_at,
                end=note.updated_at,
                type=cls.event_type,
            )
            for note in notes
        ]


class OrderTaskCalendarProvider:
    event_type = "order_task"

    @classmethod
    def get_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        deadlines = (
            OrderTaskDeadline.objects
            .filter(
                Q(
                    started_at__gte=start,
                    started_at__lt=end,
                )
                |
                Q(
                    deadline__gte=start,
                    deadline__lt=end,
                )
            )
            .select_related(
                "order_task",
            )
            .prefetch_related(
                "order_task__assigned_employee",
            )
        )

        if user.type != User.UserType.ADMIN:
            deadlines = deadlines.filter(
                Q(order_task__assigned_employee__user=user)
                |
                Q(order_task__created_by=user)
            ).distinct()

        return [
            CalendarEvent(
                id=deadline.order_task.id,
                title=deadline.order_task.title,
                start=deadline.started_at,
                end=deadline.deadline,
                type=cls.event_type,
                people={
                    "assigned_employee": [
                        employee_to_calendar_person(employee)
                        for employee
                        in deadline.order_task.assigned_employee.all()
                    ],
                },
            )
            for deadline in deadlines
        ]


class InternalTaskRoutineCalendarProvider:
    event_type = "internal_task_routine"

    @classmethod
    def get_events(
        cls,
        user,
        start: datetime,
        end: datetime,
    ) -> List[CalendarEvent]:

        routines = (
            InternalTaskRoutine.objects
            .filter(
                is_active=True,
                next_run_at__lt=end,
                task__in=InternalTaskAccess.get_queryset(user),
            )
            .select_related(
                "task",
                "task__created_by",
            )
            .prefetch_related(
                "task__assigned_to",
            )
        )

        events = []

        for routine in routines:
            occurrence = routine.next_run_at

            while occurrence < end:
                if occurrence >= start:
                    event_id = (
                        routine.id * 100_000
                        + int(occurrence.timestamp())
                    )

                    events.append(
                        CalendarEvent(
                            id=event_id,
                            title=routine.task.title,
                            start=occurrence,
                            end=None,
                            type=cls.event_type,
                            people={
                                "assigned_to": [
                                    user_to_calendar_person(assigned_user)
                                    for assigned_user
                                    in routine.task.assigned_to.all()
                                ],
                                "created_by": user_to_calendar_person(
                                    routine.task.created_by
                                ),
                            },
                        )
                    )

                occurrence += timedelta(
                    days=routine.interval_days
                )

        return events