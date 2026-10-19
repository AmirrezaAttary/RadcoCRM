# production/reports.py
import jdatetime
from django.db.models import Sum, F
from .models import ProductionLog


def jalali_month_range(year, month):
    start = jdatetime.date(year, month, 1).togregorian()
    if month == 12:
        nxt = jdatetime.date(year + 1, 1, 1)
    else:
        nxt = jdatetime.date(year, month + 1, 1)
    return start, nxt.togregorian()  # end انحصاری است


def monthly_report(year, month):
    start, end = jalali_month_range(year, month)
    logs = (ProductionLog.objects
            .filter(date__gte=start, date__lt=end)
            .select_related("operator", "machine")
            .order_by("operator__full_name", "machine__name", "date"))

    report = {}
    for log in logs:
        op = report.setdefault(log.operator_id, {
            "operator": log.operator, "machines": {},
            "total_hours": 0, "total_produced": 0, "total_waste": 0,
        })
        m = op["machines"].setdefault(log.machine_id, {
            "machine": log.machine, "days": [],
            "hours": 0, "produced": 0, "waste": 0,
        })
        m["days"].append({
            "date": jdatetime.date.fromgregorian(date=log.date),
            "hours": log.hours_worked,
            "produced": log.produced_qty,
            "waste": log.waste_qty,
            "efficiency": log.efficiency,
        })
        m["hours"] += log.hours_worked
        m["produced"] += log.produced_qty
        m["waste"] += log.waste_qty
        op["total_hours"] += log.hours_worked
        op["total_produced"] += log.produced_qty
        op["total_waste"] += log.waste_qty
    return list(report.values())