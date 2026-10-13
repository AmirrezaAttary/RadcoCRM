from django.db import transaction
from django.utils import timezone

from score.models import Score
from tasks.models import TaskStepDeadline
from warehouse.models.warehouse_order_task import OrderTaskDeadline
from notifications.sms import send_sms


SCORE_DEDUCTION_PER_24_HOURS = 5

OVERDUE_PERIOD_SECONDS = 24 * 60 * 60


def process_overdue_scores():

    now = timezone.now()

    processed = 0

    processed += process_task_step_deadlines(now=now)

    processed += process_order_task_deadlines(now=now)

    return processed


def process_task_step_deadlines(now):

    deadlines = (
        TaskStepDeadline.objects
        .select_related(
            "task",
            "department_step",
        )
        .prefetch_related(
            "task__assigned_employee",
        )
        .filter(
            deadline__isnull=False,
            deadline__lt=now,
        )
    )

    processed = 0

    for deadline_obj in deadlines:
        processed += process_task_step_deadline(
            deadline_obj=deadline_obj,
            now=now,
        )

    return processed


def process_order_task_deadlines(now):

    deadlines = (
        OrderTaskDeadline.objects
        .select_related(
            "order_task",
        )
        .prefetch_related(
            "order_task__assigned_employee",
        )
        .filter(
            deadline__isnull=False,
            deadline__lt=now,
        )
    )

    processed = 0

    for deadline_obj in deadlines:
        processed += process_order_task_deadline(
            deadline_obj=deadline_obj,
            now=now,
        )

    return processed


@transaction.atomic
def process_task_step_deadline(deadline_obj, now):

    overdue_period = calculate_overdue_period(
        deadline=deadline_obj.deadline,
        now=now,
    )

    if overdue_period <= 0:
        return 0

    task = deadline_obj.task
    department_step = deadline_obj.department_step

    employees = task.assigned_employee.all()

    created_count = 0

    for employee in employees:
        for period in range(1, overdue_period + 1):

            _, created = create_task_score(
                employee=employee,
                task=task,
                department_step=department_step,
                period=period,
            )

            if created:
                created_count += 1

    return created_count


@transaction.atomic
def process_order_task_deadline(deadline_obj, now):

    overdue_period = calculate_overdue_period(
        deadline=deadline_obj.deadline,
        now=now,
    )

    if overdue_period <= 0:
        return 0

    order_task = deadline_obj.order_task

    employees = order_task.assigned_employee.all()

    created_count = 0

    for employee in employees:
        for period in range(1, overdue_period + 1):

            _, created = create_order_task_score(
                employee=employee,
                order_task=order_task,
                period=period,
            )

            if created:
                created_count += 1

    return created_count


def calculate_overdue_period(deadline, now):

    elapsed = now - deadline

    return int(
        elapsed.total_seconds() // OVERDUE_PERIOD_SECONDS
    )


def create_task_score(
    employee,
    task,
    department_step,
    period,
):

    amount = SCORE_DEDUCTION_PER_24_HOURS

    reason = (
        f"تسک «{task.title}» در مرحله "
        f"«{department_step.name}» در مهلت تعیین‌شده انجام نشده است. "
        f"این رکورد مربوط به دوره تأخیر شماره {period} "
        f"(24 ساعت کامل پس از Deadline) است."
    )

    score, created = Score.objects.get_or_create(
        employee=employee,
        task=task,
        department_step=department_step,
        overdue_period=period,
        defaults={
            "amount": amount,
            "reason": reason,
        },
    )

    if created and employee.user.phone_number:

        message = (
            f"کارمند گرامی، به دلیل تأخیر در انجام تسک "
            f"«{task.title}» در مرحله «{department_step.name}»، "
            f"{amount} امتیاز از امتیاز شما کسر شد."
        )

        try:
            pass
        except Exception:
            pass

    return score, created


def create_order_task_score(
    employee,
    order_task,
    period,
):

    amount = SCORE_DEDUCTION_PER_24_HOURS

    reason = (
        f"تسک سفارش «{order_task.title}» "
        f"در مهلت تعیین‌شده انجام نشده است. "
        f"این رکورد مربوط به دوره تأخیر شماره {period} "
        f"(24 ساعت کامل پس از Deadline) است."
    )

    score, created = Score.objects.get_or_create(
        employee=employee,
        order_task=order_task,
        overdue_period=period,
        defaults={
            "amount": amount,
            "reason": reason,
        },
    )

    if created and employee.user.phone_number:

        message = (
            f"کارمند گرامی، به دلیل تأخیر در انجام تسک سفارش "
            f"«{order_task.title}»، "
            f"{amount} امتیاز از امتیاز شما کسر شد."
        )

        try:
            pass
        except Exception:
            pass

    return score, created