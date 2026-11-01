import secrets
import string

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum

from warehouse.models.product import Product


def generate_password(length=10):
    """رمز تصادفی خوانا (بدون حروف/ارقام مشابه مثل O/0 و l/1)."""
    alphabet = "".join(
        c for c in string.ascii_letters + string.digits if c not in "O0Il1"
    )
    return "".join(secrets.choice(alphabet) for _ in range(length))


def products_with_stock():
    """
    کالاهایی که مجموع موجودی‌شان در انبارهای «فعال» بیشتر از صفر است،
    همراه با فیلد available_quantity.
    """
    return Product.objects.annotate(
        available_quantity=Sum(
            "inventory_stocks__current_quantity",
            filter=Q(inventory_stocks__warehouse__is_active=True),
        )
    ).filter(available_quantity__gt=0)


# ───────────── ارسال سفارش به انبارها و همگام‌سازی وضعیت ─────────────

_EPS = 1e-9


class PortalConfigError(Exception):
    """مشکل پیکربندی (مثلاً دپارتمان/مرحله‌ی تسک تعریف نشده)."""


def _task_department_and_step():
    from department.models import Department

    department_id = getattr(settings, "CUSTOMER_PORTAL_TASK_DEPARTMENT_ID", None)

    if department_id:
        department = Department.objects.filter(pk=department_id).first()
    else:
        department = Department.objects.order_by("order").first()

    if department is None:
        raise PortalConfigError("هیچ دپارتمانی برای ساخت تسک سفارش مشتری تعریف نشده است.")

    step = department.steps.order_by("order").first()
    if step is None:
        raise PortalConfigError(f"دپارتمان «{department.name}» هیچ مرحله‌ای ندارد.")

    return department, step


def _allocate(items):
    """
    تخصیص هر کالا به انبارها (اول انباری که موجودی بیشتری دارد؛ در صورت
    نیاز بین چند انبار تقسیم می‌شود).
    خروجی: {Warehouse: [{"product": ..., "quantity": ...}, ...]}
    """
    from warehouse.models.warehouse_process import InventoryStock

    plan = {}

    for item in items:
        product, remaining = item["product"], item["quantity"]

        stocks = (
            InventoryStock.objects
            .select_for_update(of=("self",))
            .select_related("warehouse")
            .filter(
                product=product,
                warehouse__is_active=True,
                current_quantity__gt=0,
            )
            .order_by("-current_quantity", "warehouse_id")
        )

        for stock in stocks:
            take = min(remaining, stock.current_quantity)
            plan.setdefault(stock.warehouse, []).append(
                {"product": product, "quantity": take}
            )
            remaining -= take
            if remaining <= _EPS:
                break

        if remaining > _EPS:
            raise ValueError(
                f"موجودی «{product.name}» برای تأمین این سفارش کافی نیست."
            )

    return plan


@transaction.atomic
def dispatch_to_warehouses(order, creator):
    """
    بعد از تأیید کارمند صدا زده می‌شود. creator = کارمند تأییدکننده.
    برای سفارش مشتری یک پرونده + تسک اصلی می‌سازد و به ازای هر انبار
    یک «تسک سفارش انبار» (OrderTask) ایجاد می‌کند. انبارداران همان انبار
    پیامک می‌گیرند و با دکمه‌ی «تایید» موجود در سیستم آن را تأیید می‌کنند.
    """
    from tasks.models import Case, Task
    from warehouse.services.warehouse_order_task import OrderTaskService

    plan = _allocate([
        {"product": i.product, "quantity": i.quantity}
        for i in order.items.select_related("product")
    ])

    department, step = _task_department_and_step()
    title = f"سفارش پرتال #{order.pk} - {order.customer.full_name}"

    case = Case.objects.create(
        customer=order.customer,
        title=title,
        description=order.note,
        created_by=creator,
    )

    task = Task.objects.create(
        title=title,
        description=order.note,
        case=case,
        department=department,
        current_step=step,
        created_by=creator,
    )

    order.task = task
    order.status = order.Status.IN_WAREHOUSE
    order.save(update_fields=["task", "status", "updated_at"])

    for warehouse, items in plan.items():
        OrderTaskService.create(
            task=task,
            warehouse=warehouse,
            items=items,
            note=order.note,
        )

    return task


def refresh_order_status(order):
    """وضعیت سفارش مشتری را از روی تسک‌های انبار محاسبه و ذخیره می‌کند."""
    from warehouse.models.warehouse_order_task import OrderTask, OrderTaskItem

    # فقط سفارش‌هایی که به انبار رفته‌اند (قبل از تأیید کارمند یا رد شده توسط کارمند، تسکی ندارند)
    if order.task_id is None or order.status == order.Status.PENDING:
        return

    if OrderTask.objects.filter(
        task_id=order.task_id, status=OrderTask.Status.IN_PROGRESS
    ).exists():
        new_status = order.Status.IN_WAREHOUSE
    else:
        items = list(OrderTaskItem.objects.filter(order_task__task_id=order.task_id))

        supplied = [i for i in items if i.status == OrderTaskItem.Status.SUCCESS]
        fully = [i for i in supplied if i.completed_quantity + _EPS >= i.quantity]

        if not supplied:
            new_status = order.Status.REJECTED
        elif len(fully) == len(items):
            new_status = order.Status.CONFIRMED
        else:
            new_status = order.Status.PARTIAL

    if new_status != order.status:
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
