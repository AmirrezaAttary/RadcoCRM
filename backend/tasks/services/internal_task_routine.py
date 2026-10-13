from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from notifications.sms import send_sms

from tasks.models import (
    InternalTask,
    InternalTaskRoutine,
    InternalTaskDeadline,
)


@transaction.atomic
def create_internal_task_routine(
    *,
    task,
    start_at,
    interval_days,
):
    task = (
        InternalTask.objects
        .select_for_update()
        .get(
            pk=task.pk,
        )
    )

    if interval_days <= 0:
        raise ValueError(
            "فاصله تکرار باید بیشتر از صفر باشد."
        )

    if start_at is None:
        raise ValueError(
            "زمان شروع روتین مشخص نشده است."
        )

    if hasattr(task, "routine"):
        raise ValueError(
            "این تسک از قبل دارای روتین است."
        )


    InternalTaskDeadline.objects.filter(
        task=task,
    ).delete()

    # ---------------------------------------------------------
    # Create Routine
    # ---------------------------------------------------------

    routine = InternalTaskRoutine.objects.create(
        task=task,
        start_at=start_at,
        interval_days=interval_days,
        next_run_at=start_at,
    )

    if task.status != InternalTask.Status.WAITING:

        task.status = InternalTask.Status.WAITING
        task.completed_at = None

        task.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    return routine


@transaction.atomic
def update_internal_task_routine(
    *,
    routine,
    start_at=None,
    interval_days=None,
    is_active=None,
):
    routine = (
        InternalTaskRoutine.objects
        .select_for_update()
        .select_related("task")
        .get(
            pk=routine.pk,
        )
    )

    # ---------------------------------------------------------
    # start_at
    # ---------------------------------------------------------

    if start_at is not None:

        routine.start_at = start_at

        routine.next_run_at = start_at

    # ---------------------------------------------------------
    # interval_days
    # ---------------------------------------------------------

    if interval_days is not None:

        if interval_days <= 0:
            raise ValueError(
                "فاصله تکرار باید بیشتر از صفر باشد."
            )

        routine.interval_days = interval_days

    # ---------------------------------------------------------
    # is_active
    # ---------------------------------------------------------

    if is_active is not None:

        routine.is_active = is_active

    routine.save(
        update_fields=[
            "start_at",
            "interval_days",
            "next_run_at",
            "is_active",
            "updated_at",
        ]
    )

    return routine


@transaction.atomic
def delete_internal_task_routine(
    *,
    routine,
):
    routine = (
        InternalTaskRoutine.objects
        .select_for_update()
        .select_related("task")
        .get(
            pk=routine.pk,
        )
    )

    task = routine.task

    routine.delete()

    if task.status == InternalTask.Status.WAITING:
        task.status = InternalTask.Status.IN_PROGRESS
        task.completed_at = None

        task.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    return task


@transaction.atomic
def activate_due_routine(
    *,
    routine_id,
):
    routine = (
        InternalTaskRoutine.objects
        .select_for_update()
        .select_related("task")
        .get(
            pk=routine_id,
        )
    )

    now = timezone.now()

    if not routine.is_active:
        return None

    if routine.next_run_at > now:
        return None

    task = routine.task

    if task.status != InternalTask.Status.WAITING:
        return None

    execution_started_at = routine.next_run_at

    next_run_at = (
        routine.next_run_at
        + timedelta(
            days=routine.interval_days,
        )
    )

    while next_run_at <= now:
        next_run_at += timedelta(
            days=routine.interval_days,
        )

    task.status = InternalTask.Status.IN_PROGRESS
    task.completed_at = None

    task.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    routine.last_run_at = execution_started_at
    routine.next_run_at = next_run_at

    routine.save(
        update_fields=[
            "last_run_at",
            "next_run_at",
            "updated_at",
        ]
    )

    return task


@transaction.atomic
def activate_due_routines():
    now = timezone.now()

    routine_ids = list(
        InternalTaskRoutine.objects
        .filter(
            is_active=True,
            next_run_at__lte=now,
            task__status=InternalTask.Status.WAITING,
        )
        .values_list(
            "id",
            flat=True,
        )
    )

    activated_tasks = []

    for routine_id in routine_ids:

        task = activate_due_routine(
            routine_id=routine_id,
        )

        if task:
            activated_tasks.append(task)

            message = (
                f"تسک روتین «{task.title}» "
                f"برای شما فعال شد. "
                f"لطفاً در اسرع وقت آن را انجام دهید."
            )

            for user in task.assigned_to.all():

                if user.phone_number and user.is_active:
                    send_sms(
                        number=user.phone_number,
                        message=message,
                    )

    return activated_tasks