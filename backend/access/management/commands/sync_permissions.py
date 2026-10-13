from django.core.management.base import BaseCommand
from django.db import transaction

from access.models import Permission
from access.registry.permissions import registry


class Command(BaseCommand):
    help = "Synchronize registered permissions with the database."

    @transaction.atomic
    def handle(self, *args, **options):
        registered_permissions = registry.all()

        created_count = 0
        updated_count = 0

        for definition in registered_permissions:
            permission, created = Permission.objects.update_or_create(
                code=definition.code,
                defaults={
                    "resource": definition.resource,
                    "action": definition.action,
                    "name": definition.name,
                    "description": definition.description,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {permission.code}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    f"Updated: {permission.code}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Synchronization completed. "
                f"Created: {created_count}, "
                f"Updated: {updated_count}."
            )
        )