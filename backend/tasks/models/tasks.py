from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .cases import Case
from department.models import DepartmentStep


class Task(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "در حال انجام"
        COMPLETED = "completed", "تکمیل‌شده"
        CANCELLED = "cancelled", "لغو‌شده"
        SOLD = "sold", "به فروش رسیده"

    title = models.CharField(max_length=255, verbose_name="عنوان", default="Untitled")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    case = models.ForeignKey(
        Case,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="پرونده",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        "department.Department",
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="دپارتمان",
    )
    current_step = models.ForeignKey(
        "department.DepartmentStep",
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="مرحله‌ی فعلی",
    )
    assigned_employee = models.ManyToManyField(
        "accounts.Employee",
        related_name="assigned_tasks",
        verbose_name="کارمندان مسئول",
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name="وضعیت",
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tasks",
        verbose_name="ایجادکننده",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تسک"
        verbose_name_plural = "تسک‌ها"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["case"],
                condition=models.Q(status="in_progress", case__isnull=False),
                name="unique_active_task_per_case",
            )
        ]

    def __str__(self):
        case_title = self.case.title if self.case else "بدون پرونده"
        return f"{self.title} / {case_title} / {self.department.name}"

    def clean(self):
        from department.models import DepartmentEmployee

        if self.department_id and self.pk:
            invalid = self.assigned_employee.exclude(
                department_memberships__department_id=self.department_id
            )
            if invalid.exists():
                raise ValidationError("یک یا چند کارمند انتخاب‌شده عضو این دپارتمان نیستند.")


class TaskStepLog(models.Model):

    class Action(models.TextChoices):
        ADVANCED = "advanced", "پیشروی"
        REVERTED = "reverted", "بازگشت"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="step_logs",
        verbose_name="تسک",
    )
    step = models.ForeignKey(
        "department.DepartmentStep",
        on_delete=models.PROTECT,
        related_name="task_logs",
        verbose_name="مرحله",
    )
    employee = models.ManyToManyField(
        "accounts.Employee",
        related_name="task_step_actions",
        verbose_name="کارمندان",
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name="نوع اکشن",
    )
    note = models.TextField(blank=True, verbose_name="توضیح")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "لاگ مرحله‌ی تسک"
        verbose_name_plural = "لاگ‌های مرحله‌ی تسک"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_id} - {self.step.name} - {self.get_action_display()}"


class TaskStepDeadline(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='step_deadlines')
    department_step = models.ForeignKey(DepartmentStep, on_delete=models.CASCADE, related_name='task_deadlines')
    started_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    sms_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ('task', 'department_step')

    def __str__(self):
        return f"Task {self.task_id} - Step {self.department_step_id} - {self.deadline}"