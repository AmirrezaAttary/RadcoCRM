"""
ابزارهای بازه‌ی زمانی داشبورد (تقویم شمسی، ساعت تهران).

weekly  → ۷ روز اخیر (هر روز یک ستون)
monthly → ماه شمسی جاری (هر روز یک ستون)
yearly  → سال شمسی جاری (هر ماه یک ستون)
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import jdatetime
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

TEHRAN = ZoneInfo("Asia/Tehran")

PERIODS = ("weekly", "monthly", "yearly")

JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


@dataclass
class Bucket:
    key: str
    label: str
    start: date  # شروع (شامل) به میلادی
    end: date    # پایان (انحصاری) به میلادی


@dataclass
class Period:
    name: str
    start: datetime   # aware
    end: datetime     # aware، انحصاری
    buckets: list


def today_local() -> date:
    return timezone.now().astimezone(TEHRAN).date()


def _to_dt(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=TEHRAN)


def _jalali_month_start(year: int, month: int) -> date:
    return jdatetime.date(year, month, 1).togregorian()


def _next_month(year: int, month: int):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def jalali_month_bounds(year: int, month: int):
    ny, nm = _next_month(year, month)
    return _to_dt(_jalali_month_start(year, month)), _to_dt(_jalali_month_start(ny, nm))


def current_month_bounds():
    j = jdatetime.date.fromgregorian(date=today_local())
    return jalali_month_bounds(j.year, j.month)


def previous_month_bounds():
    j = jdatetime.date.fromgregorian(date=today_local())
    y, m = (j.year - 1, 12) if j.month == 1 else (j.year, j.month - 1)
    return jalali_month_bounds(y, m)


def build_period(name: str) -> Period:
    if name not in PERIODS:
        name = "monthly"

    today = today_local()
    j_today = jdatetime.date.fromgregorian(date=today)

    if name == "weekly":
        first = today - timedelta(days=6)
        buckets = []
        for i in range(7):
            d = first + timedelta(days=i)
            jd = jdatetime.date.fromgregorian(date=d)
            buckets.append(Bucket(
                key=d.isoformat(),
                label=str(jd.day),
                start=d,
                end=d + timedelta(days=1),
            ))
        return Period(name, _to_dt(first), _to_dt(today + timedelta(days=1)), buckets)

    if name == "monthly":
        start_d = _jalali_month_start(j_today.year, j_today.month)
        ny, nm = _next_month(j_today.year, j_today.month)
        end_d = _jalali_month_start(ny, nm)
        buckets = []
        d = start_d
        while d < end_d:
            jd = jdatetime.date.fromgregorian(date=d)
            buckets.append(Bucket(d.isoformat(), str(jd.day), d, d + timedelta(days=1)))
            d += timedelta(days=1)
        return Period(name, _to_dt(start_d), _to_dt(end_d), buckets)

    # yearly
    buckets = []
    for m in range(1, 13):
        s = _jalali_month_start(j_today.year, m)
        ny, nm = _next_month(j_today.year, m)
        e = _jalali_month_start(ny, nm)
        buckets.append(Bucket(f"{j_today.year}-{m:02d}", JALALI_MONTHS[m - 1], s, e))
    return Period(name, _to_dt(buckets[0].start), _to_dt(buckets[-1].end), buckets)


def daily_counts(queryset, field: str, period: Period) -> dict:
    """تعداد رکوردها به تفکیک روز (به وقت تهران) → {date: count}"""
    rows = (
        queryset
        .filter(**{f"{field}__gte": period.start, f"{field}__lt": period.end})
        .annotate(_day=TruncDate(field, tzinfo=TEHRAN))
        .values("_day")
        .annotate(c=Count("pk"))
    )
    return {r["_day"]: r["c"] for r in rows}


def series_for(queryset, field: str, period: Period) -> list:
    per_day = daily_counts(queryset, field, period)
    points = []
    for b in period.buckets:
        total = sum(c for d, c in per_day.items() if b.start <= d < b.end)
        points.append({"key": b.key, "label": b.label, "value": total})
    return points


def percent_change(current: int, previous: int) -> dict:
    if previous == 0:
        value = 100.0 if current > 0 else 0.0
    else:
        value = (current - previous) / previous * 100
    direction = "up" if value > 0 else "down" if value < 0 else "flat"
    return {"percent": round(abs(value)), "direction": direction}
