"""
سرویس‌های داشبورد — این اپ مدل ندارد و فقط از مدل‌های اپ‌های دیگر می‌خواند.
"""
from django.db.models import Count, Q

from accounts.models import Employee
from customers.models import Customer
from department.models import Department, DepartmentEmployee
from tasks.models import Task, TaskArchive

from .periods import (
    build_period,
    current_month_bounds,
    percent_change,
    previous_month_bounds,
    series_for,
)


class DashboardService:

    # ------------------------------------------------------------------
    # کارت‌های بالای صفحه
    # ------------------------------------------------------------------
    @classmethod
    def summary(cls):
        cur_start, cur_end = current_month_bounds()
        prev_start, prev_end = previous_month_bounds()

        # --- تعداد کارمندان (فعال) ---
        employees_now = Employee.objects.filter(is_active=True).count()
        employees_prev = Employee.objects.filter(
            is_active=True, created_at__lt=cur_start
        ).count()

        # --- مشتریان فعال (بالفعل) ---
        total_customers = Customer.objects.count()
        active_customers = Customer.objects.filter(
            status=Customer.CustomerStatus.ACTIVE
        ).count()
        active_rate = (
            round(active_customers / total_customers * 100) if total_customers else 0
        )
        new_active_cur = Customer.objects.filter(
            status=Customer.CustomerStatus.ACTIVE,
            created_at__gte=cur_start, created_at__lt=cur_end,
        ).count()
        new_active_prev = Customer.objects.filter(
            status=Customer.CustomerStatus.ACTIVE,
            created_at__gte=prev_start, created_at__lt=prev_end,
        ).count()

        # --- پروژه‌های در حال انجام ---
        projects_now = Task.objects.filter(status=Task.Status.IN_PROGRESS).count()
        # تخمین وضعیت پایان ماه قبل: تسک‌هایی که قبل از شروع ماه ساخته شده‌اند
        # و یا هنوز در جریان‌اند یا بعد از شروع ماه بسته شده‌اند.
        projects_prev = Task.objects.filter(created_at__lt=cur_start).filter(
            Q(status=Task.Status.IN_PROGRESS) | Q(updated_at__gte=cur_start)
        ).count()

        return {
            "employees": {
                "count": employees_now,
                "change": percent_change(employees_now, employees_prev),
            },
            "active_customers": {
                "count": active_customers,
                "total": total_customers,
                "percent": active_rate,
                "change": percent_change(new_active_cur, new_active_prev),
            },
            "projects_in_progress": {
                "count": projects_now,
                "change": percent_change(projects_now, projects_prev),
            },
        }

    # ------------------------------------------------------------------
    # نمودار فروش
    # ------------------------------------------------------------------
    @classmethod
    def sales_chart(cls, period_name):
        period = build_period(period_name)
        sold = TaskArchive.objects.filter(status=Task.Status.SOLD)
        points = series_for(sold, "archived_at", period)
        total = sum(p["value"] for p in points)
        return {
            "period": period.name,
            "total": total,
            "empty": total == 0,
            "points": points,
        }

    # ------------------------------------------------------------------
    # بیشترین منابع مشتری
    # ------------------------------------------------------------------
    @classmethod
    def customer_sources(cls, period_name):
        # در تب «هفتگی» همان ۷ روز اخیر، و در بقیه ماه/سال جاری
        period = build_period(period_name)
        rows = (
            Customer.objects
            .filter(created_at__gte=period.start, created_at__lt=period.end)
            .values("source")
            .annotate(c=Count("pk"))
            .order_by("-c")
        )

        merged = {}
        for r in rows:
            name = (r["source"] or "").strip() or "نامشخص"
            merged[name] = merged.get(name, 0) + r["c"]

        total = sum(merged.values())
        items = [
            {
                "name": name,
                "count": count,
                "percent": round(count / total * 100, 1) if total else 0,
            }
            for name, count in sorted(merged.items(), key=lambda x: -x[1])
        ]
        return {"period": period.name, "total": total, "items": items}

    # ------------------------------------------------------------------
    # دپارتمان‌های با بیشترین لغو تسک
    # ------------------------------------------------------------------
    @classmethod
    def cancelled_by_department(cls, period_name):
        period = build_period(period_name)
        rows = (
            TaskArchive.objects
            .filter(
                status=Task.Status.CANCELLED,
                archived_at__gte=period.start,
                archived_at__lt=period.end,
            )
            .values("department_id")
            .annotate(c=Count("pk"))
        )
        counts = {r["department_id"]: r["c"] for r in rows}

        items = [
            {"department_id": d.id, "name": d.name, "count": counts.get(d.id, 0)}
            for d in Department.objects.all()
        ]
        items.sort(key=lambda x: (-x["count"], x["name"]))
        return {
            "period": period.name,
            "total": sum(i["count"] for i in items),
            "items": items,
        }

    # ------------------------------------------------------------------
    # برترین کارشناسان (جذب مشتری بالفعل)
    # ------------------------------------------------------------------
    @classmethod
    def top_experts(cls, period_name, limit=5):
        period = build_period(period_name)
        rows = list(
            Customer.objects
            .filter(
                status=Customer.CustomerStatus.ACTIVE,
                created_at__gte=period.start,
                created_at__lt=period.end,
            )
            .values("created_by_id")
            .annotate(c=Count("pk"))
            .order_by("-c")
        )
        total = sum(r["c"] for r in rows)

        user_ids = [r["created_by_id"] for r in rows[:limit]]
        employees = {
            e.user_id: e
            for e in Employee.objects.filter(user_id__in=user_ids).select_related("user")
        }
        memberships = {}
        for m in (
            DepartmentEmployee.objects
            .filter(employee__user_id__in=user_ids)
            .select_related("department", "employee")
            .order_by("-is_manager", "id")
        ):
            memberships.setdefault(m.employee.user_id, m.department.name)

        from django.contrib.auth import get_user_model
        users = {u.id: u for u in get_user_model().objects.filter(id__in=user_ids)}

        items = []
        for rank, r in enumerate(rows[:limit], start=1):
            uid = r["created_by_id"]
            emp = employees.get(uid)
            name = emp.full_name if emp else (users[uid].username if uid in users else "—")
            items.append({
                "rank": rank,
                "employee_id": emp.id if emp else None,
                "name": name,
                "initial": name[:1],
                "department": memberships.get(uid),
                "customers": r["c"],
                "percent": round(r["c"] / total * 100) if total else 0,
            })
        return {"period": period.name, "total": total, "items": items}

    # ------------------------------------------------------------------
    # همه‌ی بخش‌ها در یک درخواست
    # ------------------------------------------------------------------
    @classmethod
    def overview(cls, sales="monthly", sources="weekly", cancelled="monthly", experts="monthly"):
        return {
            "summary": cls.summary(),
            "sales_chart": cls.sales_chart(sales),
            "customer_sources": cls.customer_sources(sources),
            "cancelled_by_department": cls.cancelled_by_department(cancelled),
            "top_experts": cls.top_experts(experts),
        }
