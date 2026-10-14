
from django.db import transaction
from django.utils import timezone

from tasks.models import (
    InternalTask,
    InternalTaskArchive,
    InternalTaskAttachment,
    InternalTaskDeadline,
    InternalTaskRoutine,
)


def _serialize_datetime(value):
    return value.isoformat() if value else None


def _delete_internal_task_deadline(*, task):
    InternalTaskDeadline.objects.filter(
        task=task,
    ).delete()


def _delete_internal_task_routine(*, task):
    InternalTaskRoutine.objects.filter(
        task=task,
    ).delete()


def _create_internal_task_archive(
    *,
    task,
    final_action_by,
    execution_started_at=None,
):
    task = (
        InternalTask.objects
        .select_related(
            "created_by",
            "created_by__employee_profile",
        )
        .prefetch_related(
            "assigned_to__employee_profile",
            "attachments__uploaded_by",
        )
        .get(
            pk=task.pk,
        )
    )

    assigned_employees_snapshot = []

    for user in task.assigned_to.all():
        employee = getattr(
            user,
            "employee_profile",
            None,
        )

        assigned_employees_snapshot.append({
            "id": user.id,
            "user_id": user.id,
            "username": user.username,
            "full_name": (
                employee.full_name
                if employee
                else ""
            ),
            "created_at": _serialize_datetime(
                employee.created_at
                if employee
                else None
            ),
            "updated_at": _serialize_datetime(
                employee.updated_at
                if employee
                else None
            ),
        })

    deadline = getattr(
        task,
        "deadline",
        None,
    )

    deadline_snapshot = {}

    if deadline:
        deadline_snapshot = {
            "id": deadline.id,
            "started_at": _serialize_datetime(
                deadline.started_at,
            ),
            "deadline": _serialize_datetime(
                deadline.deadline,
            ),
        }

    attachments_snapshot = []

    for attachment in task.attachments.all():
        uploaded_by = attachment.uploaded_by

        attachments_snapshot.append({
            "id": attachment.id,
            "file": (
                attachment.file.name
                if attachment.file
                else None
            ),
            "original_file_name": (
                attachment.original_file_name
            ),
            "note": attachment.note or "",
            "uploaded_by_id": (
                uploaded_by.id
                if uploaded_by
                else None
            ),
            "uploaded_by_username": (
                uploaded_by.username
                if uploaded_by
                else None
            ),
            "created_at": _serialize_datetime(
                attachment.created_at,
            ),
        })

    created_by = task.created_by

    created_employee = (
        getattr(
            created_by,
            "employee_profile",
            None,
        )
        if created_by
        else None
    )

    final_employee = (
        getattr(
            final_action_by,
            "employee_profile",
            None,
        )
        if final_action_by
        else None
    )

    return InternalTaskArchive.objects.create(
        task_id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        task_created_at=task.created_at,
        task_updated_at=task.updated_at,
        execution_started_at=execution_started_at,
        completed_at=task.completed_at,
        assigned_employees_snapshot=(
            assigned_employees_snapshot
        ),
        deadline_snapshot=deadline_snapshot,
        attachments_snapshot=attachments_snapshot,
        created_by_id=(
            created_by.id
            if created_by
            else None
        ),
        created_by_username=(
            created_by.username
            if created_by
            else None
        ),
        created_by_full_name=(
            created_employee.full_name
            if created_employee
            else ""
        ),
        final_action_by_id=(
            final_action_by.id
            if final_action_by
            else None
        ),
        final_action_by_username=(
            final_action_by.username
            if final_action_by
            else None
        ),
        final_action_by_full_name=(
            final_employee.full_name
            if final_employee
            else ""
        ),
    )


@transaction.atomic
def deactivate_internal_task(*, task):
    task = (
        InternalTask.objects
        .select_for_update()
        .get(
            pk=task.pk,
        )
    )

    if not task.active:
        raise ValueError(
            "این تسک از قبل غیرفعال است."
        )

    task.active = False

    if task.status == InternalTask.Status.WAITING:
        task.status = InternalTask.Status.IN_PROGRESS

    task.save(
        update_fields=[
            "active",
            "status",
            "updated_at",
        ]
    )

    _delete_internal_task_deadline(
        task=task,
    )

    _delete_internal_task_routine(
        task=task,
    )

    return task


@transaction.atomic
def activate_internal_task(*, task):
    task = (
        InternalTask.objects
        .select_for_update()
        .get(
            pk=task.pk,
        )
    )

    if task.active:
        raise ValueError(
            "این تسک از قبل فعال است."
        )

    task.active = True

    task.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return task


@transaction.atomic
def finalize_internal_task(
    *,
    task,
    final_action_by,
    status,
    attachment_files=None,
    attachment_note="",
    uploaded_by=None,
):
    task = (
        InternalTask.objects
        .select_for_update()
        .get(
            pk=task.pk,
        )
    )

    if not task.active:
        raise ValueError(
            "این تسک غیرفعال است و امکان نهایی کردن آن وجود ندارد."
        )

    if task.status != InternalTask.Status.IN_PROGRESS:
        raise ValueError(
            "فقط تسک‌های در حال انجام قابل نهایی شدن هستند."
        )

    if status not in (
        InternalTask.Status.COMPLETED,
        InternalTask.Status.CANCELLED,
    ):
        raise ValueError(
            "وضعیت نهایی نامعتبر است."
        )

    routine = getattr(
        task,
        "routine",
        None,
    )

    execution_started_at = (
        routine.last_run_at
        if routine
        else None
    )

    task.status = status

    task.completed_at = (
        timezone.now()
        if status == InternalTask.Status.COMPLETED
        else None
    )

    task.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    attachment_files = attachment_files or []

    if attachment_files:
        if uploaded_by is None:
            raise ValueError(
                "آپلودکننده فایل مشخص نشده است."
            )

        for attachment_file in attachment_files:
            InternalTaskAttachment.objects.create(
                task=task,
                file=attachment_file,
                note=attachment_note,
                uploaded_by=uploaded_by,
            )

    archive = _create_internal_task_archive(
        task=task,
        final_action_by=final_action_by,
        execution_started_at=execution_started_at,
    )

    _delete_internal_task_deadline(
        task=task,
    )

    if (
        routine
        and routine.is_active
        and status == InternalTask.Status.COMPLETED
    ):
        task.status = InternalTask.Status.WAITING
        task.completed_at = None

        task.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

    return task, archive


@transaction.atomic
def reopen_internal_task(*, task):
    task = (
        InternalTask.objects
        .select_for_update()
        .get(
            pk=task.pk,
        )
    )

    if not task.active:
        raise ValueError(
            "این تسک غیرفعال است و امکان بازگشایی آن وجود ندارد."
        )

    if task.status not in (
        InternalTask.Status.COMPLETED,
        InternalTask.Status.CANCELLED,
    ):
        raise ValueError(
            "فقط تسک‌های تکمیل‌شده یا لغوشده قابل بازگشایی هستند."
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

    return task
