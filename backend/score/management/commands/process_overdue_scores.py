from django.core.management.base import BaseCommand

from score.services.overdue import process_overdue_scores


class Command(BaseCommand):
    help = "پردازش Deadlineهای منقضی‌شده و کسر امتیاز از مسئولان تسک"

    def handle(self, *args, **options):
        created_count = process_overdue_scores()

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} رکورد امتیاز ثبت شد."
            )
        )