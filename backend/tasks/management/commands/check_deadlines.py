from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tasks.models import TaskStepDeadline
from tasks.services.deadline_sms import send_task_deadline_sms


class Command(BaseCommand):
    help = "Send SMS notifications for expired task deadlines."

    def handle(self, *args, **options):
        now = timezone.now()

        deadlines = (
            TaskStepDeadline.objects
            .select_related(
                "task",
                "task__department",
                "department_step",
            )
            .filter(
                deadline__lte=now,
                sms_sent_at__isnull=True,
                task__status="in_progress",
            )
        )

        count = 0

        for deadline in deadlines:
            try:
                with transaction.atomic():
                    deadline = (
                        TaskStepDeadline.objects
                        .select_for_update()
                        .select_related("task")
                        .get(pk=deadline.pk)
                    )

                    if deadline.sms_sent_at is not None:
                        continue

                    if deadline.task.status != "in_progress":
                        continue

                    send_task_deadline_sms(deadline)

                    deadline.sms_sent_at = timezone.now()
                    deadline.save(
                        update_fields=["sms_sent_at"]
                    )

                    count += 1

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Deadline {deadline.pk}: {exc}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} deadline SMS notification(s) sent."
            )
        )