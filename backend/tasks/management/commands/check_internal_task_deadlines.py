from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications.sms import send_sms
from tasks.models import InternalTask, InternalTaskDeadline


class Command(BaseCommand):

    def handle(self, *args, **options):

        now = timezone.now()

        deadlines = (
            InternalTaskDeadline.objects
            .select_related("task")
            .prefetch_related("task__assigned_to")
            .filter(
                deadline__lte=now,
                sms_sent_at__isnull=True,
                task__status=InternalTask.Status.IN_PROGRESS,
            )
        )

        sent_count = 0

        for deadline in deadlines:

            task = deadline.task

            users = task.assigned_to.filter(
                is_active=True,
            )

            message = (
                f"مهلت انجام تسک «{task.title}» "
                f"به پایان رسیده است."
                f"شماتا 24 ساعت آینده وقت دارد این تسک را انجام دهد در غیر این صورت از شما امتیاز کسر مشود "
            )

            sent = False

            for user in users:

                if not user.phone_number:
                    continue

                send_sms(
                    number=user.phone_number,
                    message=message,
                )

                sent = True

            if sent:
                deadline.sms_sent_at = now
                deadline.save(
                    update_fields=["sms_sent_at"]
                )

                sent_count += 1

        self.stdout.write(
            f"{sent_count} internal task deadline SMS notification(s) sent."
        )