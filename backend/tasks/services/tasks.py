from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from department.models import (
    Department,
    DepartmentEmployee,
    DepartmentStep,
)
from accounts.models import Employee
from customers.models import Customer, CustomerScore
from notifications.sms import send_sms

from ..exceptions import (
    ActiveTaskExistsError,
    EmployeeNotInDepartmentError,
    FirstStepRevertError,
    InvalidTaskActionError,
    NotDepartmentManagerError,
)
from ..models import (
    Task,
    TaskStepLog,
    TaskStepDeadline,
    TaskArchive,
    Case,
)
from .attachments import _create_attachments

def _get_first_step(department):
    return DepartmentStep.objects.filter(
        department=department
    ).order_by("order").first()

def _get_step_by_order(department, order):
    return DepartmentStep.objects.filter(
        department=department,
        order=order,
    ).first()

def _delete_task_step_deadline(*, task, department_step):
    TaskStepDeadline.objects.filter(
        task=task,
        department_step=department_step,
    ).delete()

def _delete_task_deadlines(*, task):
    TaskStepDeadline.objects.filter(
        task=task
    ).delete()

def _delete_deadlines_if_task_inactive(*, task):
    if task.status != Task.Status.IN_PROGRESS:
        _delete_task_deadlines(task=task)

def _ensure_task_workflow_active(*, task):
    # بررسی فیلدهای active طبق درخواست حذف شده است.
    return None

def _ensure_employee_active_for_department(*, employee, department):
    membership = (
        DepartmentEmployee.objects
        .select_for_update()
        .filter(
            employee=employee,
            department=department,
        )
        .first()
    )

    if membership is None:
        raise EmployeeNotInDepartmentError(
            "این کارمند عضو دپارتمان تسک نیست."
        )

    return membership

def _ensure_task_assigned_employee_active(*, task, employee):
    if not task.assigned_employee.filter(
        pk=employee.pk
    ).exists():
        raise InvalidTaskActionError(
            "شما مسئول این تسک نیستید."
        )

    return _ensure_employee_active_for_department(
        employee=employee,
        department=task.department,
    )

def _resolve_department_step(*, department, step):
    """
    مرحله‌ی انتخاب‌شده را بررسی می‌کند که متعلق به دپارتمان باشد.
    """
    if step.department_id != department.id:
        raise InvalidTaskActionError(
            "مرحله‌ی انتخاب‌شده متعلق به دپارتمان این تسک نیست."
        )

    return step


def _ensure_department_manager(*, employee, department):
    is_manager = DepartmentEmployee.objects.filter(
        employee=employee,
        department=department,
        is_manager=True,
    ).exists()

    if not is_manager:
        raise NotDepartmentManagerError()


def _get_step_employees_for_revert(*, task, step):
    """
    کارمند(های) مسئول مرحله‌ی `step` را برمی‌گرداند؛ یعنی کسانی که
    آخرین بار این مرحله را به مرحله‌ی بعد فرستاده‌اند.
    فقط کسانی که هنوز فعال و عضو دپارتمان تسک هستند در نظر گرفته می‌شوند.
    """
    last_log = (
        TaskStepLog.objects
        .filter(
            task=task,
            step=step,
            action=TaskStepLog.Action.ADVANCED,
        )
        .order_by("-created_at", "-id")
        .first()
    )

    if last_log is None:
        return []

    return list(
        Employee.objects
        .filter(
            pk__in=last_log.employee.values_list("pk", flat=True),
            is_active=True,
            department_memberships__department=task.department,
        )
        .select_related("user")
        .distinct()
    )


def _validate_assigned_employees(department, assigned_employee):
    assigned_employee = list(assigned_employee)

    if not assigned_employee:
        raise EmployeeNotInDepartmentError(
            "حداقل یک کارمند باید برای تسک انتخاب شود."
        )

    assigned_employee_ids = {
        employee.id
        for employee in assigned_employee
    }

    memberships = list(
        DepartmentEmployee.objects
        .select_for_update()
        .filter(
            department=department,
            employee_id__in=assigned_employee_ids,
        )
    )

    memberships_by_employee = {
        membership.employee_id: membership
        for membership in memberships
    }

    missing_employee_ids = (
        assigned_employee_ids
        - set(memberships_by_employee.keys())
    )

    if missing_employee_ids:
        raise EmployeeNotInDepartmentError(
            "یک یا چند کارمند انتخاب‌شده عضو این دپارتمان نیستند."
        )

    return assigned_employee

def _create_customer_score(*, task, created_by, score, reason):
    if not task.case or not task.case.customer:
        if score is not None:
            pass
        return None

    if score is None:
        raise InvalidTaskActionError(
            "برای تغییر وضعیت تسک، ثبت امتیاز مشتری الزامی است."
        )

    if not 0 <= score <= 5:
        raise InvalidTaskActionError(
            "امتیاز مشتری باید بین ۰ تا ۵ باشد."
        )

    if not reason or not reason.strip():
        raise InvalidTaskActionError(
            "دلیل امتیازدهی به مشتری الزامی است."
        )

    return CustomerScore.objects.create(
        customer=task.case.customer,
        created_by=created_by,
        score=score,
        reason=reason.strip(),
    )

def _serialize_datetime(value):
    return value.isoformat() if value else None

def _create_task_archive(*, task, final_action_by):
    task = (
        Task.objects
        .select_related(
            "case",
            "case__customer",
            "case__created_by",
            "department",
            "current_step",
            "created_by",
            "created_by__employee_profile",
        )
        .prefetch_related(
            "case__resources",
            "department__steps",
            "assigned_employee__user__employee_profile",
            "step_logs__step",
            "step_logs__employee__user__employee_profile",
            "step_logs__attachments",
            "attachments",
            "step_deadlines__department_step",
        )
        .get(pk=task.pk)
    )

    case = task.case
    customer = case.customer if case else None
    department = task.department
    current_step = task.current_step

    case_resources = [
        {
            "id": resource.id,
            "title": resource.title,
        }
        for resource in case.resources.all()
    ] if case else []

    department_steps = [
        {
            "id": step.id,
            "name": step.name,
            "description": step.description or "",
            "order": step.order,
            "created_at": _serialize_datetime(step.created_at),
            "updated_at": _serialize_datetime(step.updated_at),
        }
        for step in department.steps.all()
    ]

    assigned_employees = []

    for employee in task.assigned_employee.all():
        user = getattr(employee, "user", None)

        assigned_employees.append({
            "id": employee.id,
            "full_name": (
                employee.user.employee_profile.full_name
                if employee.user and employee.user.employee_profile
                else ""
            ),
            "user_id": user.id if user else None,
            "username": user.username if user else None,
            "created_at": _serialize_datetime(employee.created_at),
            "updated_at": _serialize_datetime(employee.updated_at),
        })

    step_logs = []

    for step_log in task.step_logs.all():
        employees = []

        for employee in step_log.employee.all():
            user = getattr(employee, "user", None)

            employees.append({
                "id": employee.id,
                "full_name": (
                    employee.user.employee_profile.full_name
                    if employee.user and employee.user.employee_profile
                    else ""
                ),
                "user_id": user.id if user else None,
                "username": user.username if user else None,
            })

        step_logs.append({
            "id": step_log.id,
            "step_id": step_log.step_id,
            "step_name": (
                step_log.step.name
                if step_log.step
                else None
            ),
            "step_description": (
                step_log.step.description
                if step_log.step
                else ""
            ),
            "step_order": (
                step_log.step.order
                if step_log.step
                else None
            ),
            "action": step_log.action,
            "action_display": step_log.get_action_display(),
            "note": step_log.note or "",
            "employees": employees,
            "created_at": _serialize_datetime(
                step_log.created_at
            ),
        })

    deadlines = [
        {
            "id": deadline.id,
            "department_step_id": deadline.department_step_id,
            "department_step_name": (
                deadline.department_step.name
                if deadline.department_step
                else None
            ),
            "department_step_order": (
                deadline.department_step.order
                if deadline.department_step
                else None
            ),
            "started_at": _serialize_datetime(
                deadline.started_at
            ),
            "deadline": _serialize_datetime(
                deadline.deadline
            ),
        }
        for deadline in task.step_deadlines.all()
    ]

    attachments = []

    for attachment in task.attachments.all():
        uploaded_by = attachment.uploaded_by

        attachments.append({
            "id": attachment.id,
            "source": "task",
            "task_id": attachment.task_id,
            "task_step_log_id": None,
            "file": (
                attachment.file.name
                if attachment.file
                else None
            ),
            "original_file_name": attachment.original_file_name,
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
                attachment.created_at
            ),
        })

    for step_log in task.step_logs.all():
        for attachment in step_log.attachments.all():
            uploaded_by = attachment.uploaded_by

            attachments.append({
                "id": attachment.id,
                "source": "step_log",
                "task_id": None,
                "task_step_log_id": step_log.id,
                "file": (
                    attachment.file.name
                    if attachment.file
                    else None
                ),
                "original_file_name": (
                    attachment.original_file_name
                ),
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
                    attachment.created_at
                ),
            })

    customer_scores = []
    if customer:
        for score in customer.scores.all():
            created_by = score.created_by

            customer_scores.append({
                "id": score.id,
                "score": score.score,
                "reason": score.reason,
                "created_by_id": (
                    created_by.id
                    if created_by
                    else None
                ),
                "created_by_full_name": (
                    created_by.user.employee_profile.full_name
                    if created_by
                    and created_by.user
                    and created_by.user.employee_profile
                    else None
                ),
                "created_at": _serialize_datetime(
                    score.created_at
                ),
            })

    created_by = task.created_by

    created_by_id = (
        created_by.id
        if created_by
        else None
    )

    created_by_username = (
        created_by.username
        if created_by
        else None
    )

    created_by_full_name = None

    if created_by:
        employee_profile = getattr(
            created_by,
            "employee_profile",
            None,
        )

        if employee_profile:
            created_by_full_name = employee_profile.full_name

    final_action_by_id = None
    final_action_by_username = None
    final_action_by_full_name = None

    if final_action_by:
        final_action_by_id = final_action_by.id

        final_action_by_user = getattr(
            final_action_by,
            "user",
            None,
        )

        final_action_by_username = (
            final_action_by_user.username
            if final_action_by_user
            else None
        )

        final_action_by_full_name = (
            final_action_by.user.employee_profile.full_name
            if final_action_by.user
            and final_action_by.user.employee_profile
            else None
        )

    current_step_id = (
        current_step.id
        if current_step
        else None
    )

    current_step_name = (
        current_step.name
        if current_step
        else None
    )

    current_step_description = (
        current_step.description
        if current_step
        else None
    )

    current_step_order = (
        current_step.order
        if current_step
        else None
    )

    customer_status_display = None

    if customer and customer.status is not None:
        customer_status_display = dict(
            Customer.CustomerStatus.choices
        ).get(
            customer.status,
            customer.status,
        )

    return TaskArchive.objects.create(
        task_id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        task_created_at=task.created_at,
        task_updated_at=task.updated_at,
        completed_at=task.completed_at,

        case_id=case.id if case else None,
        case_title=case.title if case else "",
        case_description=case.description if case else "",
        case_created_by_id=(
            case.created_by.id
            if case and case.created_by
            else None
        ),
        case_created_by_username=(
            case.created_by.username
            if case and case.created_by
            else None
        ),
        case_created_at=case.created_at if case else None,
        case_updated_at=case.updated_at if case else None,
        case_resources=case_resources,

        customer_id=customer.id if customer else None,
        customer_full_name=customer.full_name if customer else "",
        customer_job_title=customer.job_title if customer else "",
        customer_phone_number=customer.phone_number if customer else "",
        customer_company_name=customer.company_name if customer else "",
        customer_address=customer.address if customer else "",
        customer_source=customer.source if customer else "",
        customer_description=customer.description if customer else "",
        customer_status=customer.status if customer else None,
        customer_status_display=customer_status_display,
        customer_created_at=customer.created_at if customer else None,
        customer_updated_at=customer.updated_at if customer else None,

        department_id=department.id,
        department_name=department.name,
        department_order=department.order,
        department_description=department.description,

        current_step_id=current_step_id,
        current_step_name=current_step_name,
        current_step_description=current_step_description,
        current_step_order=current_step_order,

        department_steps_snapshot=department_steps,
        assigned_employees_snapshot=assigned_employees,
        step_logs_snapshot=step_logs,
        deadlines_snapshot=deadlines,
        attachments_snapshot=attachments,
        customer_scores_snapshot=customer_scores,

        created_by_id=created_by_id,
        created_by_username=created_by_username,
        created_by_full_name=created_by_full_name,

        final_action_by_id=final_action_by_id,
        final_action_by_username=final_action_by_username,
        final_action_by_full_name=final_action_by_full_name,
    )

@transaction.atomic
def create_task(
    *,
    title,
    description,
    case=None,  
    department,
    assigned_employee,
    created_by,
    files=None,
    current_step=None,
):
    assigned_employee = _validate_assigned_employees(
        department=department,
        assigned_employee=assigned_employee,
    )

    if case is not None:
        has_in_progress_task = (
            Task.objects
            .select_for_update()
            .filter(
                case=case,
                status=Task.Status.IN_PROGRESS,
            )
            .exists()
        )

        if has_in_progress_task:
            raise ActiveTaskExistsError(
                "این پرونده در حال حاضر یک تسک فعال دارد."
            )

    # اگر مرحله‌ای انتخاب نشده باشد، تسک در اولین مرحله قرار می‌گیرد.
    if current_step is None:
        start_step = _get_first_step(department)

        if start_step is None:
            raise InvalidTaskActionError(
                "این دپارتمان هیچ مرحله‌ای ندارد."
            )
    else:
        start_step = _resolve_department_step(
            department=department,
            step=current_step,
        )

    task = Task.objects.create(
        title=title,
        description=description,
        case=case,
        department=department,
        current_step=start_step,
        created_by=created_by,
    )

    task.assigned_employee.set(
        assigned_employee
    )

    message = (
        f"تسک «{task.title}» به شما اختصاص داده شد."
    )

    for employee in assigned_employee:
        if employee.user.phone_number:
            send_sms(
                number=employee.user.phone_number,
                message=message,
            )

    if files:
        _create_attachments(
            files=files,
            uploaded_by=created_by,
            task=task,
        )

    return task

@transaction.atomic
def advance_step(
    *,
    task,
    employee,
    note="",
    files=None,
    score=None,
    score_reason="",
    next_assigned_employee=None,
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "department",
            "current_step",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidTaskActionError(
            "این تسک در حال انجام نیست."
        )

    _ensure_task_assigned_employee_active(
        task=task,
        employee=employee,
    )

    current_step = task.current_step

    next_step = _get_step_by_order(
        task.department,
        current_step.order + 1,
    )

    # اگر مرحله‌ی بعدی وجود دارد، مسئول مرحله‌ی بعد باید انتخاب شود
    # (می‌تواند خود کاربر باشد). این اعتبارسنجی قبل از ثبت هر تغییری انجام می‌شود.
    new_assignees = []

    if next_step is not None:
        if not next_assigned_employee:
            raise InvalidTaskActionError(
                "برای انتقال تسک به مرحله‌ی بعد، انتخاب مسئول مرحله‌ی بعد الزامی است."
            )

        new_assignees = _validate_assigned_employees(
            department=task.department,
            assigned_employee=next_assigned_employee,
        )

    step_log = TaskStepLog.objects.create(
        task=task,
        step=current_step,
        action=TaskStepLog.Action.ADVANCED,
        note=note,
    )

    step_log.employee.add(employee)

    if files:
        _create_attachments(
            files=files,
            uploaded_by=employee.user,
            task_step_log=step_log,
        )

    if next_step is None:
        _create_customer_score(
            task=task,
            created_by=employee,
            score=score,
            reason=score_reason,
        )

        task.status = Task.Status.COMPLETED
        task.completed_at = timezone.now()

    else:
        _delete_task_step_deadline(
            task=task,
            department_step=current_step,
        )

        task.current_step = next_step

        # مسئول‌های مرحله‌ی قبل جایگزین مسئول(های) انتخاب‌شده می‌شوند.
        task.assigned_employee.set(new_assignees)

    task.save(
        update_fields=[
            "status",
            "completed_at",
            "current_step",
            "updated_at",
        ]
    )

    if new_assignees:
        message = (
            f"تسک «{task.title}» به مرحله‌ی «{next_step.name}» "
            f"منتقل شد و به شما اختصاص داده شد."
        )

        for assignee in new_assignees:
            if assignee.user.phone_number:
                send_sms(
                    number=assignee.user.phone_number,
                    message=message,
                )

    if (
        task.status == Task.Status.COMPLETED
        and task.department.order == 1
        and task.case
        and task.case.customer
        and task.case.customer.status
        == Customer.CustomerStatus.POTENTIAL
    ):
        customer = task.case.customer

        customer.status = (
            Customer.CustomerStatus.ACTIVE
        )

        customer.save(
            update_fields=["status"]
        )

    if task.status == Task.Status.COMPLETED:
        _create_task_archive(
            task=task,
            final_action_by=employee,
        )

        _delete_deadlines_if_task_inactive(
            task=task
        )

    return task

@transaction.atomic
def complete_task(
    *,
    task,
    employee,
    note="",
    files=None,
    score=None,
    score_reason="",
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "department",
            "current_step",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidTaskActionError(
            "فقط تسک‌های در حال انجام قابل تکمیل هستند."
        )

    _ensure_task_assigned_employee_active(
        task=task,
        employee=employee,
    )

    _create_customer_score(
        task=task,
        created_by=employee,
        score=score,
        reason=score_reason,
    )

    step_log = TaskStepLog.objects.create(
        task=task,
        step=task.current_step,
        action=TaskStepLog.Action.ADVANCED,
        note=note,
    )

    step_log.employee.add(employee)

    if files:
        _create_attachments(
            files=files,
            uploaded_by=employee.user,
            task_step_log=step_log,
        )

    task.status = Task.Status.COMPLETED
    task.completed_at = timezone.now()

    task.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    if (
        task.department.order == 1
        and task.case
        and task.case.customer
        and task.case.customer.status
        == Customer.CustomerStatus.POTENTIAL
    ):
        customer = task.case.customer

        customer.status = (
            Customer.CustomerStatus.ACTIVE
        )

        customer.save(
            update_fields=["status"]
        )

    _create_task_archive(
        task=task,
        final_action_by=employee,
    )

    _delete_deadlines_if_task_inactive(
        task=task,
    )

    return task

@transaction.atomic
def revert_step(
    *,
    task,
    employee,
    note="",
    files=None,
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "current_step",
            "department",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidTaskActionError(
            "این تسک در حال انجام نیست."
        )

    _ensure_task_assigned_employee_active(
        task=task,
        employee=employee,
    )

    if task.current_step.order <= 1:
        raise FirstStepRevertError(
            "این تسک در اولین مرحله است و امکان بازگشت ندارد."
        )

    current_step = task.current_step

    previous_step = _get_step_by_order(
        task.department,
        current_step.order - 1,
    )

    if previous_step is None:
        raise FirstStepRevertError(
            "مرحله قبلی برای این تسک پیدا نشد."
        )

    # مسئول مرحله‌ی قبل را قبل از ثبت لاگ برگشت پیدا می‌کنیم.
    previous_assignees = _get_step_employees_for_revert(
        task=task,
        step=previous_step,
    )

    step_log = TaskStepLog.objects.create(
        task=task,
        step=current_step,
        action=TaskStepLog.Action.REVERTED,
        note=note,
    )

    step_log.employee.add(employee)

    if files:
        _create_attachments(
            files=files,
            uploaded_by=employee.user,
            task_step_log=step_log,
        )

    _delete_task_step_deadline(
        task=task,
        department_step=current_step,
    )

    task.current_step = previous_step

    # تسک به همان فردی برمی‌گردد که مرحله‌ی قبل را انجام داده بود.
    # اگر چنین فردی پیدا نشد (مثلاً دیگر در دپارتمان نیست)،
    # مسئول‌های فعلی تغییری نمی‌کنند تا تسک بدون مسئول نماند.
    if previous_assignees:
        task.assigned_employee.set(previous_assignees)

    task.save(
        update_fields=[
            "current_step",
            "updated_at",
        ]
    )

    if previous_assignees:
        message = (
            f"تسک «{task.title}» به مرحله‌ی «{previous_step.name}» "
            f"بازگردانده شد و به شما اختصاص داده شد."
        )

        for assignee in previous_assignees:
            if assignee.user.phone_number:
                send_sms(
                    number=assignee.user.phone_number,
                    message=message,
                )

    return task

@transaction.atomic
def cancel_task(
    *,
    task,
    cancelled_by,
    score=None,
    score_reason="",
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "department",
            "current_step",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidTaskActionError(
            "فقط تسک‌های در حال انجام قابل لغو هستند."
        )

    _ensure_task_assigned_employee_active(
        task=task,
        employee=cancelled_by,
    )

    _create_customer_score(
        task=task,
        created_by=cancelled_by,
        score=score,
        reason=score_reason,
    )

    task.status = Task.Status.CANCELLED

    task.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    _create_task_archive(
        task=task,
        final_action_by=cancelled_by,
    )

    _delete_deadlines_if_task_inactive(
        task=task
    )

    return task

@transaction.atomic
def sell_task(
    *,
    task,
    employee,
    score=None,
    score_reason="",
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "department",
            "current_step",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    if task.status != Task.Status.IN_PROGRESS:
        raise InvalidTaskActionError(
            "فقط تسک‌های در حال انجام قابل فروش هستند."
        )

    _ensure_task_assigned_employee_active(
        task=task,
        employee=employee,
    )

    _create_customer_score(
        task=task,
        created_by=employee,
        score=score,
        reason=score_reason,
    )

    task.status = Task.Status.SOLD

    task.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    _create_task_archive(
        task=task,
        final_action_by=employee,
    )

    _delete_deadlines_if_task_inactive(
        task=task
    )

    return task

def set_task_step_deadline(
    task_id,
    department_step_id,
    started_at=None,
    deadline=None,
):
    task = get_object_or_404(
        Task.objects.select_related(
            "department",
            "current_step",
        ),
        id=task_id,
    )

    _ensure_task_workflow_active(
        task=task
    )

    department_step = get_object_or_404(
        DepartmentStep,
        id=department_step_id,
    )

    if department_step.department_id != task.department_id:
        raise InvalidTaskActionError(
            "این مرحله متعلق به دپارتمان تسک نیست."
        )

    obj, _ = TaskStepDeadline.objects.update_or_create(
        task=task,
        department_step=department_step,
        defaults={
            "started_at": started_at,
            "deadline": deadline,
        },
    )

    return obj

def get_task_step_deadline(
    task_id,
    department_step_id,
):
    return get_object_or_404(
        TaskStepDeadline,
        task_id=task_id,
        department_step_id=department_step_id,
    )

@transaction.atomic
def reopen_task(
    *,
    task,
    employee,
    current_step,
    assigned_employee,
):
    task = (
        Task.objects
        .select_for_update()
        .select_related(
            "department",
            "current_step",
        )
        .get(pk=task.pk)
    )

    _ensure_task_workflow_active(
        task=task
    )

    # فقط مدیر دپارتمان می‌تواند تسک را از آرشیو برگرداند.
    _ensure_department_manager(
        employee=employee,
        department=task.department,
    )

    if task.status not in (
        Task.Status.COMPLETED,
        Task.Status.CANCELLED,
        Task.Status.SOLD,
    ):
        raise InvalidTaskActionError(
            "فقط تسک‌های تکمیل‌شده، لغوشده یا به فروش رسیده قابل بازگشایی هستند."
        )

    if task.case_id is not None:
        has_in_progress_task = (
            Task.objects
            .filter(
                case_id=task.case_id,
                status=Task.Status.IN_PROGRESS,
            )
            .exclude(pk=task.pk)
            .exists()
        )

        if has_in_progress_task:
            raise ActiveTaskExistsError(
                "این پرونده در حال حاضر یک تسک فعال دارد."
            )

    target_step = _resolve_department_step(
        department=task.department,
        step=current_step,
    )

    new_assignees = _validate_assigned_employees(
        department=task.department,
        assigned_employee=assigned_employee,
    )

    task.status = Task.Status.IN_PROGRESS
    task.completed_at = None
    task.current_step = target_step

    task.assigned_employee.set(new_assignees)

    task.save(
        update_fields=[
            "status",
            "completed_at",
            "current_step",
            "updated_at",
        ]
    )

    message = (
        f"تسک «{task.title}» به مرحله‌ی «{target_step.name}» "
        f"بازگردانده شد و به شما اختصاص داده شد."
    )

    for assignee in new_assignees:
        if assignee.user.phone_number:
            send_sms(
                number=assignee.user.phone_number,
                message=message,
            )

    return task

@transaction.atomic
def deactivate_task(*, task):
    task = (
        Task.objects
        .select_for_update()
        .get(pk=task.pk)
    )

    _delete_task_deadlines(
        task=task
    )

    task.active = False

    task.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return task

@transaction.atomic
def activate_task(*, task):
    task = (
        Task.objects
        .select_for_update()
        .get(pk=task.pk)
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
def deactivate_department(*, department):
    department = (
        Department.objects
        .select_for_update()
        .get(pk=department.pk)
    )

    TaskStepDeadline.objects.filter(
        task__department=department,
    ).delete()

    department.active = False

    department.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return department

@transaction.atomic
def activate_department(*, department):
    department = (
        Department.objects
        .select_for_update()
        .get(pk=department.pk)
    )

    department.active = True

    department.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return department

@transaction.atomic
def deactivate_department_step(*, department_step):
    department_step = (
        DepartmentStep.objects
        .select_for_update()
        .select_related("department")
        .get(pk=department_step.pk)
    )

    TaskStepDeadline.objects.filter(
        department_step=department_step,
    ).delete()

    department_step.active = False

    department_step.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return department_step

@transaction.atomic
def activate_department_step(*, department_step):
    department_step = (
        DepartmentStep.objects
        .select_for_update()
        .select_related("department")
        .get(pk=department_step.pk)
    )

    department_step.active = True

    department_step.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return department_step

@transaction.atomic
def deactivate_department_employee(
    *,
    department_id,
    employee_id,
):
    department_employee = (
        DepartmentEmployee.objects
        .select_for_update()
        .select_related(
            "employee",
            "department",
        )
        .filter(
            department_id=department_id,
            employee_id=employee_id,
        )
        .first()
    )

    if department_employee is None:
        raise EmployeeNotInDepartmentError(
            "این کارمند عضو این دپارتمان نیست."
        )

    tasks = (
        Task.objects
        .filter(
            department_id=department_id,
            assigned_employee=employee_id,
        )
        .prefetch_related(
            "assigned_employee",
        )
        .distinct()
    )

    department_employee.active = False

    department_employee.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    for task in tasks:
        assigned_employees = list(
            task.assigned_employee.all()
        )

        if len(assigned_employees) == 1:
            _delete_task_deadlines(
                task=task
            )
            continue

        remaining_employee_ids = [
            employee.id
            for employee in assigned_employees
            if employee.id != employee_id
        ]

        has_remaining_assigned_employee = (
            DepartmentEmployee.objects
            .filter(
                department_id=department_id,
                employee_id__in=remaining_employee_ids,
            )
            .exists()
        )

        if not has_remaining_assigned_employee:
            _delete_task_deadlines(
                task=task
            )

    return department_employee

@transaction.atomic
def activate_department_employee(
    *,
    department_id,
    employee_id,
):
    department_employee = (
        DepartmentEmployee.objects
        .select_for_update()
        .select_related(
            "employee",
            "department",
        )
        .filter(
            department_id=department_id,
            employee_id=employee_id,
        )
        .first()
    )

    if department_employee is None:
        raise EmployeeNotInDepartmentError(
            "این کارمند عضو این دپارتمان نیست."
        )

    department_employee.active = True

    department_employee.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return department_employee

@transaction.atomic
def deactivate_case(*, case):
    case = (
        Case.objects
        .select_for_update()
        .get(pk=case.pk)
    )

    case.active = False

    case.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return case

@transaction.atomic
def activate_case(*, case):
    case = (
        Case.objects
        .select_for_update()
        .get(pk=case.pk)
    )

    case.active = True

    case.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return case