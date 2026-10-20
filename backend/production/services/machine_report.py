from datetime import timedelta

import jdatetime
from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
)

from production.models.machine import Machine
from production.models.production_log import ProductionLog
from production.services.report import (
    _finalize,
    _new_bucket,
    jalali_month_range,
)


GROUP_BY_CHOICES = ("day", "week", "month", "year")

_DECIMAL = DecimalField(max_digits=20, decimal_places=4)


def jalali_year_range(year):
    """
    بازه‌ی میلادی یک سال شمسی: (شروع، پایان)؛ پایان انحصاری است.
    """
    start = jdatetime.date(year, 1, 1).togregorian()
    end = jdatetime.date(year + 1, 1, 1).togregorian()
    return start, end


def _jalali(d):
    return jdatetime.date.fromgregorian(date=d).strftime("%Y/%m/%d")


def _sums():
    return {
        "hours": Sum("hours_worked"),
        "produced": Sum("produced_qty"),
        "waste": Sum("waste_qty"),
        "expected_production": Sum(
            ExpressionWrapper(
                F("hours_worked") * F("std_production_per_hour"),
                output_field=_DECIMAL,
            )
        ),
        "expected_waste": Sum(
            ExpressionWrapper(
                F("hours_worked") * F("std_waste_per_hour"),
                output_field=_DECIMAL,
            )
        ),
    }


def _merge(bucket, row):
    bucket["hours"] += row["hours"] or 0
    bucket["produced"] += row["produced"] or 0
    bucket["waste"] += row["waste"] or 0
    bucket["expected_production"] += row["expected_production"] or 0
    bucket["expected_waste"] += row["expected_waste"] or 0


# ---------------------------------------------------------------------
# Period helpers (روز / هفته / ماه / سال بر اساس تقویم شمسی)
# ---------------------------------------------------------------------

def _bucket(d, group_by):
    """
    تاریخ میلادی d را به بازه‌ی خودش می‌نگارد: (key, شروع، پایان).
    هفته از شنبه شروع می‌شود؛ ماه و سال شمسی‌اند.
    """
    if group_by == "day":
        return d.isoformat(), d, d

    jd = jdatetime.date.fromgregorian(date=d)

    if group_by == "week":
        start = d - timedelta(days=jd.weekday())  # شنبه = 0
        return start.isoformat(), start, start + timedelta(days=6)

    if group_by == "month":
        start, end = jalali_month_range(jd.year, jd.month)
        key = f"{jd.year}/{jd.month:02d}"
    else:  # year
        start, end = jalali_year_range(jd.year)
        key = str(jd.year)

    return key, start, end - timedelta(days=1)


def _periods(date_from, date_to, group_by):
    """
    همه‌ی بازه‌های بین date_from و date_to (حتی بدون داده)،
    تا نمودار فرانت جای خالی نداشته باشد. اولین و آخرین بازه
    به محدوده‌ی درخواستی بریده می‌شوند.
    """
    periods = []
    d = date_from

    while d <= date_to:
        key, start, end = _bucket(d, group_by)

        p_from = max(start, date_from)
        p_to = min(end, date_to)

        if group_by == "day":
            label = _jalali(p_from)
        elif group_by == "week":
            label = f"{_jalali(p_from)} - {_jalali(p_to)}"
        else:
            label = key

        periods.append({
            "key": key,
            "label": label,
            "date_from": p_from,
            "date_to": p_to,
        })

        d = end + timedelta(days=1)

    return periods


def _machine_info(machine_id, name, code):
    return {
        "machine_id": machine_id,
        "machine_name": name,
        "machine_code": code,
    }


class MachineReportService:

    # -----------------------------------------------------------------
    # روند تولید دستگاه‌ها به تفکیک روز / هفته / ماه / سال
    # -----------------------------------------------------------------

    @classmethod
    def summary(cls, *, date_from, date_to, group_by="day", machine=None):

        periods = _periods(date_from, date_to, group_by)

        logs = ProductionLog.objects.filter(
            date__gte=date_from,
            date__lte=date_to,
        )

        if machine:
            logs = logs.filter(machine=machine)

        rows = (
            logs
            .values("machine_id", "machine__name", "machine__code", "date")
            .annotate(**_sums())
            .order_by("machine__name", "date")
        )

        machines = {}

        if machine:
            machines[machine.pk] = {
                "info": _machine_info(machine.pk, machine.name, machine.code),
                "total": _new_bucket(),
                "buckets": {},
            }

        grand_total = _new_bucket()

        for row in rows:
            entry = machines.setdefault(
                row["machine_id"],
                {
                    "info": _machine_info(
                        row["machine_id"],
                        row["machine__name"],
                        row["machine__code"],
                    ),
                    "total": _new_bucket(),
                    "buckets": {},
                },
            )

            key = _bucket(row["date"], group_by)[0]
            bucket = entry["buckets"].setdefault(key, _new_bucket())

            _merge(bucket, row)
            _merge(entry["total"], row)
            _merge(grand_total, row)

        result = []

        for entry in machines.values():
            period_list = []

            for p in periods:
                data = _finalize(
                    entry["buckets"].get(p["key"]) or _new_bucket()
                )
                period_list.append({
                    "key": p["key"],
                    "label": p["label"],
                    "date_from": p["date_from"].isoformat(),
                    "date_to": p["date_to"].isoformat(),
                    **data,
                })

            result.append({
                **entry["info"],
                **_finalize(entry["total"]),
                "periods": period_list,
            })

        return {
            "group_by": group_by,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),  # شامل
            "totals": _finalize(grand_total),
            "machines": result,
        }

    # -----------------------------------------------------------------
    # جمع آخر ماه هر دستگاه (با تفکیک اپراتورها)
    # -----------------------------------------------------------------

    @classmethod
    def monthly(cls, *, year, month, machine=None):

        date_from, date_to = jalali_month_range(year, month)  # انحصاری

        logs = ProductionLog.objects.filter(
            date__gte=date_from,
            date__lt=date_to,
        )

        if machine:
            logs = logs.filter(machine=machine)

        machine_rows = {
            r["machine_id"]: r
            for r in (
                logs
                .values("machine_id")
                .annotate(days_worked=Count("date", distinct=True), **_sums())
                .order_by()
            )
        }

        operator_rows = {}

        for r in (
            logs
            .values("machine_id", "employee_id", "employee__full_name")
            .annotate(**_sums())
            .order_by("employee__full_name")
        ):
            operator_rows.setdefault(r["machine_id"], []).append(r)

        if machine:
            machines = [machine]
        else:
            # همه‌ی دستگاه‌های فعال (حتی با تولید صفر) + هر دستگاهی که
            # در این ماه ثبت داشته
            machines = Machine.objects.filter(
                Q(is_active=True) | Q(pk__in=machine_rows.keys())
            ).order_by("name")

        grand_total = _new_bucket()
        result = []

        for m in machines:
            total = _new_bucket()
            days_worked = 0

            row = machine_rows.get(m.pk)
            if row:
                _merge(total, row)
                _merge(grand_total, row)
                days_worked = row["days_worked"]

            operators = []
            for r in operator_rows.get(m.pk, []):
                op = _new_bucket()
                _merge(op, r)
                operators.append({
                    "employee_id": r["employee_id"],
                    "employee_name": r["employee__full_name"],
                    **_finalize(op),
                })

            result.append({
                **_machine_info(m.pk, m.name, m.code),
                "is_active": m.is_active,
                "days_worked": days_worked,
                **_finalize(total),
                "operators": operators,
            })

        return {
            "year": year,
            "month": month,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),  # انحصاری (روز اول ماه بعد)
            "totals": _finalize(grand_total),
            "machines": result,
        }
