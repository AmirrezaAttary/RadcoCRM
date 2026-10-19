from decimal import Decimal

import jdatetime
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import Employee, User
from production.models import Machine, ProductionLog
from production.services.report import jalali_month_range


class ProductionApiTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", phone_number="09120000000",
            password="x", type=User.UserType.ADMIN,
        )
        cls.staff_user = User.objects.create_user(
            username="emp1", phone_number="09120000001", password="x",
        )
        cls.op1 = Employee.objects.create(user=cls.staff_user, full_name="Ali")
        op2_user = User.objects.create_user(
            username="emp2", phone_number="09120000002", password="x",
        )
        cls.op2 = Employee.objects.create(user=op2_user, full_name="Reza")

        cls.m1 = Machine.objects.create(
            name="Press", code="M1",
            std_production_per_hour=50, std_waste_per_hour=2,
        )
        cls.m2 = Machine.objects.create(
            name="Cutter", code="M2",
            std_production_per_hour=100, std_waste_per_hour=5,
        )

    def _log(self, date, employee, machine, hours, produced, waste):
        return self.client.post(
            reverse("production-log-create"),
            {
                "date": date, "employee": employee.pk, "machine": machine.pk,
                "hours_worked": hours, "produced_qty": produced,
                "waste_qty": waste,
            },
            format="json",
        )

    def test_non_admin_is_denied(self):
        self.client.force_authenticate(self.staff_user)
        res = self.client.get(reverse("production-machine-list"))
        self.assertEqual(res.status_code, 403)

    def test_anonymous_is_denied(self):
        res = self.client.get(reverse("production-log-list"))
        self.assertIn(res.status_code, (401, 403))

    def test_machine_crud(self):
        self.client.force_authenticate(self.admin)
        res = self.client.post(
            reverse("production-machine-create"),
            {"name": "Lathe", "code": "M3",
             "std_production_per_hour": "30", "std_waste_per_hour": "1"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        pk = res.data["id"]

        res = self.client.patch(
            reverse("production-machine-update", args=[pk]),
            {"is_active": False}, format="json",
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.get(
            reverse("production-machine-list"), {"is_active": "true"},
        )
        self.assertEqual(
            {m["code"] for m in res.data}, {"M1", "M2"},
        )

        res = self.client.delete(
            reverse("production-machine-delete", args=[pk]),
        )
        self.assertEqual(res.status_code, 204)

    def test_delete_machine_with_logs_is_blocked(self):
        self.client.force_authenticate(self.admin)
        self._log("2026-10-01", self.op1, self.m1, 8, 400, 10)
        res = self.client.delete(
            reverse("production-machine-delete", args=[self.m1.pk]),
        )
        self.assertEqual(res.status_code, 400)

    def test_log_create_and_duplicate(self):
        self.client.force_authenticate(self.admin)
        res = self._log("2026-10-01", self.op1, self.m1, 8, 400, 10)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["employee_name"], "Ali")
        self.assertEqual(res.data["efficiency"], 100.0)

        res = self._log("2026-10-01", self.op1, self.m1, 2, 10, 0)
        self.assertEqual(res.status_code, 400)

        # همان کارمند، همان روز، دستگاه دیگر مجاز است
        res = self._log("2026-10-01", self.op1, self.m2, 2, 150, 4)
        self.assertEqual(res.status_code, 201, res.data)

    def test_hours_validation(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(
            self._log("2026-10-01", self.op1, self.m1, 25, 1, 0).status_code,
            400,
        )
        self.assertEqual(
            self._log("2026-10-01", self.op1, self.m1, 0, 1, 0).status_code,
            400,
        )

    def test_inactive_machine_and_employee_rejected(self):
        self.client.force_authenticate(self.admin)
        self.m2.is_active = False
        self.m2.save()
        self.assertEqual(
            self._log("2026-10-01", self.op1, self.m2, 4, 10, 0).status_code,
            400,
        )
        self.op2.is_active = False
        self.op2.save()
        self.assertEqual(
            self._log("2026-10-01", self.op2, self.m1, 4, 10, 0).status_code,
            400,
        )

    def test_standard_snapshot_survives_machine_change(self):
        self.client.force_authenticate(self.admin)
        res = self._log("2026-10-01", self.op1, self.m1, 8, 400, 10)
        log_id = res.data["id"]

        self.m1.std_production_per_hour = Decimal("80")
        self.m1.save()

        log = ProductionLog.objects.get(pk=log_id)
        self.assertEqual(log.std_production_per_hour, Decimal("50"))
        self.assertEqual(log.expected_production, Decimal("400"))

    def test_list_filters(self):
        self.client.force_authenticate(self.admin)
        self._log("2026-10-01", self.op1, self.m1, 8, 400, 10)
        self._log("2026-10-02", self.op2, self.m2, 8, 800, 30)
        res = self.client.get(
            reverse("production-log-list"), {"employee_id": self.op2.pk},
        )
        self.assertEqual(len(res.data), 1)
        res = self.client.get(
            reverse("production-log-list"),
            {"date_from": "2026-10-02", "date_to": "2026-10-02"},
        )
        self.assertEqual(len(res.data), 1)

    def test_monthly_report(self):
        self.client.force_authenticate(self.admin)
        # 1405/07 = مهر ۱۴۰۵
        self._log("2026-10-01", self.op1, self.m1, 8, 400, 10)
        self._log("2026-10-03", self.op1, self.m1, 6, 290, 8)
        self._log("2026-10-03", self.op1, self.m2, 2, 200, 9)
        self._log("2026-10-05", self.op2, self.m2, 8, 750, 35)
        # خارج از ماه
        self._log("2026-11-20", self.op1, self.m1, 8, 400, 10)

        res = self.client.get(
            reverse("production-report-monthly"),
            {"year": 1405, "month": 7},
        )
        self.assertEqual(res.status_code, 200, res.data)
        data = res.data

        self.assertEqual(len(data["employees"]), 2)
        ali = next(e for e in data["employees"] if e["employee_name"] == "Ali")
        self.assertEqual(ali["produced"], 890)
        self.assertEqual(ali["waste"], 27)
        self.assertEqual(ali["hours"], Decimal("16"))
        self.assertEqual(len(ali["machines"]), 2)

        press = next(m for m in ali["machines"] if m["machine_code"] == "M1")
        self.assertEqual(press["produced"], 690)
        self.assertEqual(len(press["days"]), 2)
        self.assertEqual(press["days"][0]["jalali_date"], "1405/07/09")

        self.assertEqual(data["totals"]["produced"], 890 + 750)

        # فیلتر روی یک کارمند
        res = self.client.get(
            reverse("production-report-monthly"),
            {"year": 1405, "month": 7, "employee_id": self.op2.pk},
        )
        self.assertEqual(len(res.data["employees"]), 1)

    def test_report_query_validation(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(
            reverse("production-report-monthly"), {"year": 1405, "month": 13},
        )
        self.assertEqual(res.status_code, 400)

    def test_jalali_month_range(self):
        for month in range(1, 13):
            start, end = jalali_month_range(1405, month)
            self.assertLess(start, end)
        # اسفند ۱۴۰۵ تا فروردین ۱۴۰۶
        start, end = jalali_month_range(1405, 12)
        self.assertEqual(
            jdatetime.date.fromgregorian(date=end),
            jdatetime.date(1406, 1, 1),
        )
