from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import Employee, User
from customers.models import Customer, CustomerScore
from department.models import Department, DepartmentStep
from score.models import Score
from tasks.models import Case, Resource, Task, TaskStepLog, TaskStepDeadline
from warehouse.models import Product, Warehouse
from warehouse.models.warehouse_order_task import (
    OrderTask,
    OrderTaskItem,
)


class CaseReportApiTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", password="x", phone_number="09120000000",
            type=User.UserType.ADMIN,
        )
        cls.emp_user = User.objects.create_user(
            username="ali", password="x", phone_number="09120000001",
        )
        cls.employee = Employee.objects.create(user=cls.emp_user, full_name="علی رضایی")

        cls.other_user = User.objects.create_user(
            username="other", password="x", phone_number="09120000002",
        )
        Employee.objects.create(user=cls.other_user, full_name="نفر دیگر")

        cls.customer = Customer.objects.create(
            full_name="مشتری تست", phone_number="09123334444",
            created_by=cls.admin,
        )
        CustomerScore.objects.create(
            customer=cls.customer, created_by=cls.employee,
            score=4, reason="خوب",
        )

        cls.dep = Department.objects.create(name="فروش", order=1)
        cls.step1 = DepartmentStep.objects.create(department=cls.dep, name="تماس", order=1)
        cls.step2 = DepartmentStep.objects.create(department=cls.dep, name="پیشنهاد", order=2)

        cls.case = Case.objects.create(
            customer=cls.customer, title="پرونده الف", created_by=cls.admin,
        )
        cls.case.resources.add(Resource.objects.create(title="اینستاگرام"))

        cls.task = Task.objects.create(
            title="تسک ۱", case=cls.case, department=cls.dep,
            current_step=cls.step2, created_by=cls.admin,
        )
        cls.task.assigned_employee.add(cls.employee)
        t0 = timezone.now() - timedelta(days=2)
        Task.objects.filter(pk=cls.task.pk).update(created_at=t0)

        log1 = TaskStepLog.objects.create(
            task=cls.task, step=cls.step1, action="advanced", note="شروع",
        )
        log1.employee.add(cls.employee)
        TaskStepLog.objects.filter(pk=log1.pk).update(created_at=t0 + timedelta(hours=1))
        log2 = TaskStepLog.objects.create(
            task=cls.task, step=cls.step2, action="advanced", note="ادامه",
        )
        log2.employee.add(cls.employee)

        TaskStepDeadline.objects.create(
            task=cls.task, department_step=cls.step2,
            started_at=t0, deadline=timezone.now() - timedelta(hours=3),
        )
        Score.objects.create(
            employee=cls.employee, task=cls.task, department_step=cls.step2,
            amount=2, reason="تاخیر", overdue_period=1,
        )

        warehouse = Warehouse.objects.create(name="انبار مرکزی", code="W1")
        product = Product.objects.create(name="کالای الف", sale_price=1000)
        order = OrderTask.objects.create(
            task=cls.task, warehouse=warehouse, case=cls.case, title="سفارش ۱",
            department=cls.dep, current_step=cls.step2, created_by=cls.admin,
        )
        OrderTaskItem.objects.create(
            order_task=order, product=product, quantity=5,
            completed_quantity=4, product_sale_price=1000, status="success",
        )

    def url(self, case=None):
        return reverse("tasks:case_report:case-report", args=[(case or self.case).pk])

    def test_admin_gets_full_report(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(self.url())
        self.assertEqual(res.status_code, 200, res.content)
        data = res.json()

        self.assertEqual(data["case"]["title"], "پرونده الف")
        self.assertEqual(data["customer"]["scores"]["average"], 4.0)
        self.assertEqual(data["summary"]["tasks_count"], 1)
        self.assertEqual(data["summary"]["order_tasks_count"], 1)
        self.assertEqual(float(data["summary"]["total_order_amount"]), 4000)
        self.assertEqual(data["summary"]["scores"]["deducted"], 2)
        self.assertEqual(data["summary"]["overdue_steps"], 1)

        task = data["tasks"][0]
        self.assertEqual(len(task["step_logs"]), 2)
        self.assertEqual(task["counts"]["advanced"], 2)
        self.assertTrue(task["deadlines"][0]["is_overdue"])
        self.assertGreater(task["duration_seconds"], 2 * 86400 - 5)
        self.assertEqual(len(task["step_durations"]), 2)

        times = [e["at"] for e in data["timeline"]]
        self.assertEqual(times, sorted(times))

    def test_sections_filter(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(self.url(), {"sections": "summary,tasks"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(set(res.json()), {"generated_at", "summary", "tasks"})

        bad = self.client.get(self.url(), {"sections": "nope"})
        self.assertEqual(bad.status_code, 400)

    def test_assigned_employee_can_see_but_stranger_cannot(self):
        self.client.force_authenticate(self.emp_user)
        self.assertEqual(self.client.get(self.url()).status_code, 200)

        self.client.force_authenticate(self.other_user)
        self.assertEqual(self.client.get(self.url()).status_code, 403)

    def test_requires_login(self):
        self.assertIn(self.client.get(self.url()).status_code, (401, 403))

    def test_case_without_tasks(self):
        empty = Case.objects.create(
            customer=self.customer, title="خالی", created_by=self.admin,
        )
        self.client.force_authenticate(self.admin)
        data = self.client.get(self.url(empty)).json()
        self.assertEqual(data["summary"]["tasks_count"], 0)
        self.assertEqual(data["tasks"], [])
        self.assertEqual(len(data["timeline"]), 1)
