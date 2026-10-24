"""
گزارش جامع یک پرونده.

همه‌ی اطلاعات مرتبط با پرونده را یک‌جا جمع می‌کند:
مشتری، تسک‌ها و مراحل آن‌ها، مهلت‌ها، پیوست‌ها، سفارش‌های انبار،
امتیازهای کسر/افزایش‌یافته و یک تایم‌لاین کلی.

این سرویس فقط می‌خواند و چیزی در دیتابیس تغییر نمی‌دهد.
"""
from decimal import Decimal

from django.db.models import Prefetch
from django.utils import timezone

from customers.models import CustomerScore
from score.models import Score
from tasks.models import Task, TaskArchive, TaskStepLog
from warehouse.models.warehouse_order_task import OrderTask


ZERO = Decimal("0")


# ----------------------------------------------------------------------
# ابزارهای کمکی
# ----------------------------------------------------------------------
def _iso(value):
    return value.isoformat() if value else None


def _seconds_between(start, end):
    if not start or not end:
        return None
    return max(int((end - start).total_seconds()), 0)


def _user_name(user):
    if user is None:
        return None
    profile = getattr(user, "employee_profile", None)
    if profile is not None and profile.full_name:
        return profile.full_name
    return user.username


def _employee_brief(employee):
    return {
        "id": employee.id,
        "full_name": employee.full_name,
    }


def _file_url(file_field, request):
    if not file_field:
        return None
    try:
        url = file_field.url
    except ValueError:
        return None
    return request.build_absolute_uri(url) if request else url


def _score_row(score):
    return {
        "id": score.id,
        "employee": _employee_brief(score.employee),
        "action": score.action,
        "action_display": score.get_action_display(),
        "amount": score.amount,
        "reason": score.reason,
        "overdue_period": score.overdue_period,
        "step_id": score.department_step_id,
        "created_at": _iso(score.created_at),
    }


def _score_totals(scores):
    deducted = sum(s.amount for s in scores if s.action == Score.Action.DEDUCT)
    added = sum(s.amount for s in scores if s.action == Score.Action.ADD)
    return {
        "deducted": deducted,
        "added": added,
        "net": added - deducted,
    }


# ----------------------------------------------------------------------
# سرویس اصلی
# ----------------------------------------------------------------------
class CaseReportService:

    @classmethod
    def build(cls, *, case, request=None):
        now = timezone.now()

        tasks = list(cls._tasks_queryset(case))
        order_tasks = list(cls._order_tasks_queryset(case))

        archives = cls._latest_archives(tasks)

        task_rows = [
            cls._task_row(task, archives.get(task.id), now, request)
            for task in tasks
        ]
        order_rows = [
            cls._order_task_row(order_task, now, request)
            for order_task in order_tasks
        ]

        return {
            "generated_at": _iso(now),
            "case": cls._case_row(case),
            "customer": cls._customer_row(case.customer),
            "summary": cls._summary(case, tasks, task_rows, order_tasks, order_rows),
            "tasks": task_rows,
            "order_tasks": order_rows,
            "timeline": cls._timeline(task_rows, order_rows, case),
        }

    # ------------------------------------------------------------------
    # کوئری‌ها
    # ------------------------------------------------------------------
    @staticmethod
    def _tasks_queryset(case):
        return (
            Task.objects
            .filter(case=case)
            .select_related(
                "department",
                "current_step",
                "created_by",
                "created_by__employee_profile",
            )
            .prefetch_related(
                "assigned_employee",
                "attachments__uploaded_by__employee_profile",
                "step_deadlines__department_step",
                Prefetch(
                    "step_logs",
                    queryset=(
                        TaskStepLog.objects
                        .select_related("step")
                        .prefetch_related(
                            "employee",
                            "attachments__uploaded_by__employee_profile",
                        )
                        .order_by("created_at")
                    ),
                ),
                Prefetch(
                    "score_logs",
                    queryset=(
                        Score.objects
                        .select_related("employee")
                        .order_by("created_at")
                    ),
                ),
            )
            .order_by("created_at")
        )

    @staticmethod
    def _order_tasks_queryset(case):
        return (
            OrderTask.objects
            .filter(case=case)
            .select_related(
                "warehouse",
                "product",
                "department",
                "current_step",
                "created_by",
                "created_by__employee_profile",
                "performed_by__employee",
                "deadline",
            )
            .prefetch_related(
                "assigned_employee",
                "items__product",
                "attachments__performed_by__employee",
                Prefetch(
                    "score_logs",
                    queryset=(
                        Score.objects
                        .select_related("employee")
                        .order_by("created_at")
                    ),
                ),
            )
            .order_by("created_at")
        )

    @staticmethod
    def _latest_archives(tasks):
        """آخرین رکورد آرشیو هر تسک (برای ثبت‌کننده‌ی اقدام نهایی و امتیاز مشتری)."""
        task_ids = [t.id for t in tasks]
        if not task_ids:
            return {}

        result = {}
        for archive in (
            TaskArchive.objects
            .filter(task_id__in=task_ids)
            .order_by("archived_at")  # آخری روی قبلی می‌نشیند
        ):
            result[archive.task_id] = archive
        return result

    # ------------------------------------------------------------------
    # بخش‌های گزارش
    # ------------------------------------------------------------------
    @staticmethod
    def _case_row(case):
        return {
            "id": case.id,
            "title": case.title,
            "description": case.description,
            "active": case.active,
            "resources": [
                {"id": r.id, "title": r.title}
                for r in case.resources.all()
            ],
            "created_by": _user_name(case.created_by),
            "created_at": _iso(case.created_at),
            "updated_at": _iso(case.updated_at),
        }

    @staticmethod
    def _customer_row(customer):
        scores = list(
            CustomerScore.objects
            .filter(customer=customer)
            .select_related("created_by")
            .order_by("created_at")
        )
        average = (
            round(sum(s.score for s in scores) / len(scores), 2)
            if scores else None
        )
        return {
            "id": customer.id,
            "full_name": customer.full_name,
            "job_title": customer.job_title,
            "phone_number": customer.phone_number,
            "company_name": customer.company_name,
            "address": customer.address,
            "source": customer.source,
            "status": customer.status,
            "status_display": customer.get_status_display(),
            "scores": {
                "count": len(scores),
                "average": average,
                "items": [
                    {
                        "score": s.score,
                        "reason": s.reason,
                        "by": s.created_by.full_name,
                        "created_at": _iso(s.created_at),
                    }
                    for s in scores
                ],
            },
        }

    @classmethod
    def _task_row(cls, task, archive, now, request):
        end = task.completed_at or (
            task.updated_at if task.status != Task.Status.IN_PROGRESS else now
        )

        step_logs = []
        for log in task.step_logs.all():
            step_logs.append({
                "id": log.id,
                "step_id": log.step_id,
                "step_name": log.step.name if log.step_id else None,
                "action": log.action,
                "action_display": log.get_action_display(),
                "employees": [_employee_brief(e) for e in log.employee.all()],
                "note": log.note,
                "attachments": [
                    cls._attachment_row(a, request)
                    for a in log.attachments.all()
                ],
                "created_at": _iso(log.created_at),
            })

        # مدت ماندن در هر مرحله: فاصله‌ی هر لاگ تا لاگ بعدی (آخری تا پایان/اکنون)
        durations = cls._step_durations(task, end)

        deadline_rows = []
        for d in task.step_deadlines.all():
            overdue = bool(
                d.deadline
                and task.status == Task.Status.IN_PROGRESS
                and d.deadline < now
                and d.department_step_id == task.current_step_id
            )
            deadline_rows.append({
                "step_id": d.department_step_id,
                "step_name": d.department_step.name,
                "started_at": _iso(d.started_at),
                "deadline": _iso(d.deadline),
                "is_overdue": overdue,
            })

        # پیوست‌های خود تسک (نه پیوست لاگ‌ها)
        attachments = [
            cls._attachment_row(a, request)
            for a in task.attachments.all()
        ]

        scores = list(task.score_logs.all())

        row = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "status_display": task.get_status_display(),
            "active": task.active,
            "department": {
                "id": task.department_id,
                "name": task.department.name,
            },
            "current_step": {
                "id": task.current_step_id,
                "name": task.current_step.name,
            },
            "assigned_employees": [
                _employee_brief(e) for e in task.assigned_employee.all()
            ],
            "created_by": _user_name(task.created_by),
            "created_at": _iso(task.created_at),
            "completed_at": _iso(task.completed_at),
            "duration_seconds": _seconds_between(task.created_at, end),
            "final_action_by": (
                archive.final_action_by_full_name
                or archive.final_action_by_username
            ) if archive else None,
            "step_logs": step_logs,
            "step_durations": durations,
            "deadlines": deadline_rows,
            "attachments": attachments,
            "scores": {
                "totals": _score_totals(scores),
                "items": [_score_row(s) for s in scores],
            },
            "counts": {
                "advanced": sum(1 for l in step_logs if l["action"] == "advanced"),
                "reverted": sum(1 for l in step_logs if l["action"] == "reverted"),
                "transferred": sum(1 for l in step_logs if l["action"] == "transferred"),
                "attachments": len(attachments) + sum(
                    len(l["attachments"]) for l in step_logs
                ),
                "overdue_steps": sum(1 for d in deadline_rows if d["is_overdue"]),
            },
        }
        return row

    @staticmethod
    def _step_durations(task, end):
        logs = list(task.step_logs.all())
        if not logs:
            return []

        totals = {}
        names = {}
        order = []

        # شروع تسک در اولین مرحله؛ هر لاگ یعنی «به این مرحله رسید/رفت»
        # بنابراین زمان بین دو لاگ پشت‌سرهم، مدت ماندن در مرحله‌ی لاگ قبلی است.
        for index, log in enumerate(logs):
            next_time = logs[index + 1].created_at if index + 1 < len(logs) else end
            seconds = _seconds_between(log.created_at, next_time) or 0
            if log.step_id not in totals:
                totals[log.step_id] = 0
                names[log.step_id] = log.step.name if log.step_id else None
                order.append(log.step_id)
            totals[log.step_id] += seconds

        return [
            {
                "step_id": step_id,
                "step_name": names[step_id],
                "seconds": totals[step_id],
            }
            for step_id in order
        ]

    @staticmethod
    def _attachment_row(attachment, request):
        return {
            "id": attachment.id,
            "name": attachment.original_file_name,
            "url": _file_url(attachment.file, request),
            "uploaded_by": _user_name(attachment.uploaded_by),
            "created_at": _iso(attachment.created_at),
        }

    @classmethod
    def _order_task_row(cls, order_task, now, request):
        items = []
        total_amount = ZERO
        for item in order_task.items.all():
            price = item.product_sale_price
            line_total = (
                Decimal(str(item.completed_quantity)) * price
                if price is not None and item.status == item.Status.SUCCESS
                else None
            )
            if line_total is not None:
                total_amount += line_total
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "completed_quantity": item.completed_quantity,
                "unit_price": price,
                "line_total": line_total,
                "status": item.status,
                "status_display": item.get_status_display(),
                "error_message": item.error_message,
            })

        deadline = getattr(order_task, "deadline", None)
        deadline_row = None
        if deadline is not None:
            deadline_row = {
                "started_at": _iso(deadline.started_at),
                "deadline": _iso(deadline.deadline),
                "is_overdue": bool(
                    deadline.deadline
                    and order_task.status == OrderTask.Status.IN_PROGRESS
                    and deadline.deadline < now
                ),
            }

        scores = list(order_task.score_logs.all())
        performed_by = order_task.performed_by

        return {
            "id": order_task.id,
            "task_id": order_task.task_id,
            "title": order_task.title,
            "description": order_task.description,
            "note": order_task.note,
            "status": order_task.status,
            "status_display": order_task.get_status_display(),
            "warehouse": {
                "id": order_task.warehouse_id,
                "name": order_task.warehouse.name,
            },
            "department": order_task.department.name,
            "current_step": order_task.current_step.name,
            "assigned_employees": [
                _employee_brief(e) for e in order_task.assigned_employee.all()
            ],
            "performed_by": (
                performed_by.employee.full_name if performed_by else None
            ),
            "created_by": _user_name(order_task.created_by),
            "created_at": _iso(order_task.created_at),
            "file_url": _file_url(order_task.file, request),
            "items": items,
            "total_amount": total_amount,
            "deadline": deadline_row,
            "attachments": [
                {
                    "id": a.id,
                    "note": a.note,
                    "url": _file_url(a.file, request),
                    "performed_by": a.performed_by.employee.full_name,
                    "created_at": _iso(a.created_at),
                }
                for a in order_task.attachments.all()
            ],
            "scores": {
                "totals": _score_totals(scores),
                "items": [_score_row(s) for s in scores],
            },
        }

    # ------------------------------------------------------------------
    # خلاصه
    # ------------------------------------------------------------------
    @staticmethod
    def _summary(case, tasks, task_rows, order_tasks, order_rows):
        by_status = {s.value: 0 for s in Task.Status}
        for task in tasks:
            by_status[task.status] = by_status.get(task.status, 0) + 1

        order_by_status = {s.value: 0 for s in OrderTask.Status}
        for order_task in order_tasks:
            order_by_status[order_task.status] = (
                order_by_status.get(order_task.status, 0) + 1
            )

        all_scores = [
            s
            for task in tasks for s in task.score_logs.all()
        ] + [
            s
            for order_task in order_tasks for s in order_task.score_logs.all()
        ]

        employees = {}
        for row in task_rows:
            for e in row["assigned_employees"]:
                employees[e["id"]] = e
            for log in row["step_logs"]:
                for e in log["employees"]:
                    employees[e["id"]] = e
        for row in order_rows:
            for e in row["assigned_employees"]:
                employees[e["id"]] = e

        durations = [
            r["duration_seconds"] for r in task_rows
            if r["duration_seconds"] is not None
        ]

        return {
            "tasks_count": len(tasks),
            "tasks_by_status": by_status,
            "order_tasks_count": len(order_tasks),
            "order_tasks_by_status": order_by_status,
            "total_order_amount": sum(
                (r["total_amount"] for r in order_rows), ZERO
            ),
            "total_duration_seconds": sum(durations),
            "step_actions": {
                "advanced": sum(r["counts"]["advanced"] for r in task_rows),
                "reverted": sum(r["counts"]["reverted"] for r in task_rows),
                "transferred": sum(r["counts"]["transferred"] for r in task_rows),
            },
            "attachments_count": sum(r["counts"]["attachments"] for r in task_rows)
            + sum(len(r["attachments"]) for r in order_rows),
            "overdue_steps": sum(r["counts"]["overdue_steps"] for r in task_rows),
            "scores": _score_totals(all_scores),
            "involved_employees": list(employees.values()),
        }

    # ------------------------------------------------------------------
    # تایم‌لاین
    # ------------------------------------------------------------------
    @staticmethod
    def _timeline(task_rows, order_rows, case):
        events = [{
            "at": _iso(case.created_at),
            "type": "case_created",
            "title": "ایجاد پرونده",
            "detail": case.title,
        }]

        for t in task_rows:
            events.append({
                "at": t["created_at"],
                "type": "task_created",
                "title": "ایجاد تسک",
                "detail": f'{t["title"]} ({t["department"]["name"]})',
                "task_id": t["id"],
            })
            for log in t["step_logs"]:
                events.append({
                    "at": log["created_at"],
                    "type": f'step_{log["action"]}',
                    "title": log["action_display"],
                    "detail": log["step_name"],
                    "note": log["note"],
                    "employees": [e["full_name"] for e in log["employees"]],
                    "task_id": t["id"],
                })
            for s in t["scores"]["items"]:
                events.append({
                    "at": s["created_at"],
                    "type": f'score_{s["action"]}',
                    "title": s["action_display"],
                    "detail": f'{s["employee"]["full_name"]}: {s["amount"]}',
                    "note": s["reason"],
                    "task_id": t["id"],
                })
            if t["completed_at"]:
                events.append({
                    "at": t["completed_at"],
                    "type": "task_finished",
                    "title": t["status_display"],
                    "detail": t["title"],
                    "task_id": t["id"],
                })

        for o in order_rows:
            events.append({
                "at": o["created_at"],
                "type": "order_task_created",
                "title": "ایجاد تسک سفارش انبار",
                "detail": f'{o["title"]} ({o["warehouse"]["name"]})',
                "order_task_id": o["id"],
            })
            for a in o["attachments"]:
                events.append({
                    "at": a["created_at"],
                    "type": "order_task_action",
                    "title": "اقدام انبار",
                    "detail": a["performed_by"],
                    "note": a["note"],
                    "order_task_id": o["id"],
                })
            for s in o["scores"]["items"]:
                events.append({
                    "at": s["created_at"],
                    "type": f'score_{s["action"]}',
                    "title": s["action_display"],
                    "detail": f'{s["employee"]["full_name"]}: {s["amount"]}',
                    "note": s["reason"],
                    "order_task_id": o["id"],
                })

        events.sort(key=lambda e: e["at"] or "")
        return events
