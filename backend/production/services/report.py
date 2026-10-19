from decimal import Decimal

import jdatetime

from production.models.production_log import ProductionLog


ZERO = Decimal("0")


def jalali_month_range(year, month):
    """
    بازه‌ی میلادی یک ماه شمسی را برمی‌گرداند: (شروع، پایان).
    پایان انحصاری است (date < end).
    """
    start = jdatetime.date(year, month, 1)

    if month == 12:
        end = jdatetime.date(year + 1, 1, 1)
    else:
        end = jdatetime.date(year, month + 1, 1)

    return start.togregorian(), end.togregorian()


def _efficiency(produced, expected):
    if not expected:
        return None
    return round(float(produced / expected * 100), 1)


def _new_bucket():
    return {
        "hours": ZERO,
        "produced": 0,
        "waste": 0,
        "expected_production": ZERO,
        "expected_waste": ZERO,
    }


def _add(bucket, log):
    bucket["hours"] += log.hours_worked
    bucket["produced"] += log.produced_qty
    bucket["waste"] += log.waste_qty
    bucket["expected_production"] += log.expected_production
    bucket["expected_waste"] += log.expected_waste


def _finalize(bucket):
    bucket["efficiency"] = _efficiency(
        bucket["produced"],
        bucket["expected_production"],
    )
    return bucket


class ProductionReportService:

    @classmethod
    def monthly(cls, *, year, month, employee_id=None):
        """
        گزارش ماهانه: به تفکیک کارمند ← دستگاه ← روز.
        """
        date_from, date_to = jalali_month_range(year, month)

        logs = (
            ProductionLog.objects
            .filter(date__gte=date_from, date__lt=date_to)
            .select_related("employee", "machine")
            .order_by("employee__full_name", "machine__name", "date")
        )

        if employee_id:
            logs = logs.filter(employee_id=employee_id)

        employees = {}
        grand_total = _new_bucket()

        for log in logs:

            emp = employees.setdefault(
                log.employee_id,
                {
                    "employee_id": log.employee_id,
                    "employee_name": log.employee.full_name,
                    "_total": _new_bucket(),
                    "_machines": {},
                },
            )

            mac = emp["_machines"].setdefault(
                log.machine_id,
                {
                    "machine_id": log.machine_id,
                    "machine_name": log.machine.name,
                    "machine_code": log.machine.code,
                    "_total": _new_bucket(),
                    "days": [],
                },
            )

            day = _new_bucket()
            _add(day, log)
            _finalize(day)
            day["log_id"] = log.id
            day["date"] = log.date.isoformat()
            day["jalali_date"] = (
                jdatetime.date.fromgregorian(date=log.date)
                .strftime("%Y/%m/%d")
            )
            day["note"] = log.note
            mac["days"].append(day)

            _add(mac["_total"], log)
            _add(emp["_total"], log)
            _add(grand_total, log)

        result = []

        for emp in employees.values():
            machines = []

            for mac in emp.pop("_machines").values():
                machines.append({
                    "machine_id": mac["machine_id"],
                    "machine_name": mac["machine_name"],
                    "machine_code": mac["machine_code"],
                    **_finalize(mac["_total"]),
                    "days": mac["days"],
                })

            result.append({
                "employee_id": emp["employee_id"],
                "employee_name": emp["employee_name"],
                **_finalize(emp.pop("_total")),
                "machines": machines,
            })

        return {
            "year": year,
            "month": month,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "totals": _finalize(grand_total),
            "employees": result,
        }
