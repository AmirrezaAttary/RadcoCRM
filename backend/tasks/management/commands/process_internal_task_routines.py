from django.core.management.base import BaseCommand

from tasks.services.internal_task_routine import (
    activate_due_routines,
)


class Command(BaseCommand):

    help = "فعال‌سازی تسک‌های روتین سررسیدشده"

    def handle(self, *args, **options):

        tasks = activate_due_routines()

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(tasks)} routine task(s) activated."
            )
        )