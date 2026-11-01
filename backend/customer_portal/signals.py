from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from warehouse.models.warehouse_order_task import OrderTask

from .models import CustomerOrder
from .services import refresh_order_status


def _refresh_for_task(task_id):
    for order in CustomerOrder.objects.filter(task_id=task_id):
        refresh_order_status(order)


@receiver(post_save, sender=OrderTask, dispatch_uid="customer_portal_order_task_saved")
def order_task_saved(sender, instance, **kwargs):
    # بعد از commit تا وضعیت آیتم‌ها هم نهایی شده باشد
    transaction.on_commit(lambda: _refresh_for_task(instance.task_id))
