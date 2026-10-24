"""
گزارش تفاضل «تولید و ضایعات واقعی» از «استاندارد» برای نمودار،
هم به تفکیک دستگاه و هم به تفکیک اپراتور.

تفاضل همیشه «واقعی − استاندارد» است:
    production_diff > 0  → تولید بیشتر از استاندارد (خوب)
    waste_diff      > 0  → ضایعات بیشتر از استاندارد (بد)

استاندارد هر ثبت همان مقدارِ لحظه‌ی ثبت است (std_*_per_hour × ساعت کار)،
پس تغییر استاندارد دستگاه گزارش‌های گذشته را عوض نمی‌کند.
"""
from production.models.machine import Machine
from production.models.production_log import ProductionLog
from production.services.machine_report import (
    _merge,
    _periods,
    _bucket,
    _sums,
)
from production.services.report import _new_bucket


ENTITY_CHOICES = ("machine", "operator", "both")

SERIES_KEYS = (
    "produced",
    "expected_production",
    "production_diff",
    "waste",
    "expected_waste",
    "waste_diff",
)


def _num(value):
    """Decimal/int → float گرد‌شده، مناسب نمودار."""
    return round(float(value), 2)


def _percent(diff, expected):
    if not expected:
        return None
    return round(float(diff / expected * 100), 1)


def _metrics(bucket):
    produced = bucket["produced"]
    waste = bucket["waste"]
    expected_production = bucket["expected_production"]
    expected_waste = bucket["expected_waste"]

    production_diff = produced - expected_production
    waste_diff = waste - expected_waste

    return {
        "hours": _num(bucket["hours"]),
        "produced": produced,
        "expected_production": _num(expected_production),
        "production_diff": _num(production_diff),
        "production_diff_percent": _percent(
            production_diff, expected_production
        ),
        "efficiency": (
            round(float(produced / expected_production * 100), 1)
            if expected_production else None
        ),
        "waste": waste,
        "expected_waste": _num(expected_waste),
        "waste_diff": _num(waste_diff),
        "waste_diff_percent": _percent(waste_diff, expected_waste),
    }


def _entity_report(*, logs, id_field, info_fn, periods, group_by, forced):
    """
    id_field:  نام فیلد گروه‌بندی (machine_id / employee_id)
    info_fn:   row → dict مشخصات موجودیت
    forced:    اگر موجودیتی خاص فیلتر شده، حتی بدون داده برگردد
    """
    rows = (
        logs
        .values(*info_fn.fields, "date")
        .annotate(**_sums())
        .order_by(info_fn.order_by, "date")
    )

    entities = {}
    grand_total = _new_bucket()

    if forced is not None:
        entities[info_fn.forced_id(forced)] = {
            "info": info_fn.from_obj(forced),
            "total": _new_bucket(),
            "buckets": {},
        }

    for row in rows:
        entry = entities.setdefault(
            row[id_field],
            {
                "info": info_fn(row),
                "total": _new_bucket(),
                "buckets": {},
            },
        )

        key = _bucket(row["date"], group_by)[0]
        bucket = entry["buckets"].setdefault(key, _new_bucket())

        _merge(bucket, row)
        _merge(entry["total"], row)
        _merge(grand_total, row)

    items = []

    for entry in entities.values():
        period_rows = []
        series = {k: [] for k in SERIES_KEYS}

        for p in periods:
            data = _metrics(entry["buckets"].get(p["key"]) or _new_bucket())
            period_rows.append({
                "key": p["key"],
                "label": p["label"],
                "date_from": p["date_from"].isoformat(),
                "date_to": p["date_to"].isoformat(),
                **data,
            })
            for k in SERIES_KEYS:
                series[k].append(data[k])

        items.append({
            **entry["info"],
            "totals": _metrics(entry["total"]),
            "periods": period_rows,
            "series": series,
        })

    return {
        "totals": _metrics(grand_total),
        "items": items,
    }


class _MachineInfo:
    fields = ("machine_id", "machine__name", "machine__code")
    order_by = "machine__name"

    def __call__(self, row):
        return {
            "machine_id": row["machine_id"],
            "machine_name": row["machine__name"],
            "machine_code": row["machine__code"],
        }

    @staticmethod
    def forced_id(obj):
        return obj.pk

    @staticmethod
    def from_obj(obj):
        return {
            "machine_id": obj.pk,
            "machine_name": obj.name,
            "machine_code": obj.code,
        }


class _OperatorInfo:
    fields = ("employee_id", "employee__full_name")
    order_by = "employee__full_name"

    def __call__(self, row):
        return {
            "employee_id": row["employee_id"],
            "employee_name": row["employee__full_name"],
        }

    @staticmethod
    def forced_id(obj):
        return obj.pk

    @staticmethod
    def from_obj(obj):
        return {
            "employee_id": obj.pk,
            "employee_name": obj.full_name,
        }


class VarianceReportService:

    @classmethod
    def build(
        cls,
        *,
        date_from,
        date_to,
        group_by="day",
        entity="both",
        machine=None,
        employee=None,
    ):
        periods = _periods(date_from, date_to, group_by)

        logs = ProductionLog.objects.filter(
            date__gte=date_from,
            date__lte=date_to,
        )

        if machine:
            logs = logs.filter(machine=machine)

        if employee:
            logs = logs.filter(employee=employee)

        result = {
            "group_by": group_by,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),  # شامل
            # محور افقی مشترک برای همه‌ی نمودارها
            "labels": [p["label"] for p in periods],
        }

        if entity in ("machine", "both"):
            result["machines"] = _entity_report(
                logs=logs,
                id_field="machine_id",
                info_fn=_MachineInfo(),
                periods=periods,
                group_by=group_by,
                forced=machine,
            )

        if entity in ("operator", "both"):
            result["operators"] = _entity_report(
                logs=logs,
                id_field="employee_id",
                info_fn=_OperatorInfo(),
                periods=periods,
                group_by=group_by,
                forced=employee,
            )

        return result
