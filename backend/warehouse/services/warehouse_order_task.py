from django.db import transaction

from notifications.sms import send_sms

from warehouse.models.warehouse_order_task import (
    OrderTask,
    OrderTaskItem,
    OrderTaskAttachment,
    OrderTaskDeadline,
)
from warehouse.models.order_task_archive import OrderTaskArchive
from warehouse.models.warehouse_process import StockTransaction
from warehouse.models.warehouse_staff import WarehouseStaff

from .warehouse_process import InventoryService


class OrderTaskService:

    @staticmethod
    def _send_creation_sms(order_task):

        warehouse_staffs = (
            WarehouseStaff.objects
            .filter(
                is_active=True,
                employee__is_active=True,
                employee__user__is_active=True,
            )
            .select_related(
                "employee",
                "employee__user",
            )
        )

        message = (
            f"تسک جدید «{order_task.title}» "
            "در سیستم ثبت شد. "
            "لطفاً جهت مشاهده و پیگیری تسک به سامانه مراجعه کنید."
        )

        sent_count = 0

        for staff in warehouse_staffs:

            user = staff.employee.user

            phone_number = user.phone_number

            if not phone_number:
                continue

            try:
                send_sms(
                    number=phone_number,
                    message=message,
                )

                sent_count += 1

            except Exception:
                continue

        return sent_count

    @staticmethod
    def _create_archive(order_task):

        case_data = (
            {
                "id": order_task.case.id,
                "title": order_task.case.title,
            }
            if order_task.case
            else None
        )

        customer = (
            order_task.case.customer
            if order_task.case
            else None
        )

        customer_data = (
            {
                "id": customer.id,
                "full_name": customer.full_name,
            }
            if customer
            else None
        )

        department_data = (
            {
                "id": order_task.department.id,
                "name": order_task.department.name,
            }
            if order_task.department
            else None
        )

        current_step_data = (
            {
                "id": order_task.current_step.id,
                "name": order_task.current_step.name,
            }
            if order_task.current_step
            else None
        )

        created_by_data = (
            {
                "id": order_task.created_by.id,
                "username": order_task.created_by.username,
            }
            if order_task.created_by
            else None
        )

        # اطلاعات انجام‌دهنده
        # نام از Employee.full_name خوانده می‌شود
        performed_by_data = None

        if (
            order_task.performed_by
            and order_task.performed_by.employee
        ):

            employee = order_task.performed_by.employee

            performed_by_data = {
                "id": order_task.performed_by.id,
                "employee_id": employee.id,
                "full_name": employee.full_name,
            }

        # کارمندان مسئول تسک
        # دیگر از User.profile استفاده نمی‌شود
        assigned_employees_data = [
            {
                "id": employee.id,
                "full_name": employee.full_name,
            }
            for employee in order_task.assigned_employee.all()
        ]

        warehouse = order_task.warehouse

        items_data = [
            {
                "id": item.id,

                "product_id": item.product_id,

                "product_name": (
                    item.product.name
                    if item.product
                    else None
                ),

                "quantity": item.quantity,

                "completed_quantity": (
                    item.completed_quantity
                ),

                "product_sale_price": (
                    str(item.product_sale_price)
                    if item.product_sale_price is not None
                    else None
                ),

                "status": item.status,

                "status_display": (
                    item.get_status_display()
                ),

                "error_message": item.error_message,

                "stock_transaction_id": (
                    item.stock_transaction_id
                ),
            }
            for item in order_task.items.all()
        ]

        return OrderTaskArchive.objects.create(
            order_task=order_task,

            warehouse_id=(
                warehouse.id
                if warehouse
                else None
            ),

            warehouse_name=(
                warehouse.name
                if warehouse
                else None
            ),

            warehouse_code=(
                warehouse.code
                if warehouse
                else None
            ),

            task_id=order_task.task_id,
            status=order_task.status,
            title=order_task.title,
            description=order_task.description,

            product_id=order_task.product_id,

            product_name=(
                order_task.product.name
                if order_task.product
                else None
            ),

            product_sale_price=(
                order_task.product_sale_price
            ),

            quantity=order_task.quantity,

            completed_quantity=(
                order_task.completed_quantity
            ),

            items=items_data,

            case=case_data,
            customer=customer_data,
            department=department_data,
            current_step=current_step_data,
            created_by=created_by_data,
            performed_by=performed_by_data,
            assigned_employees=assigned_employees_data,

            note=order_task.note,
            completion_note=order_task.note,

            file=order_task.file,

            order_task_created_at=(
                order_task.created_at
            ),
        )

    @staticmethod
    @transaction.atomic
    def create(
        *,
        task,
        warehouse,
        items,
        note="",
        file=None,
        started_at=None,
        deadline=None,
    ):

        if not warehouse:
            raise ValueError(
                "انبار برای ایجاد تسک سفارش الزامی است."
            )

        if not items:
            raise ValueError(
                "حداقل یک کالا برای سفارش الزامی است."
            )

        product_ids = []

        for item in items:

            product = item.get("product")
            quantity = item.get("quantity")

            if not product:
                raise ValueError(
                    "کالا برای ایجاد سفارش الزامی است."
                )

            if quantity is None or quantity <= 0:
                raise ValueError(
                    "تعداد سفارش باید بیشتر از صفر باشد."
                )

            product_ids.append(product.id)

        if len(product_ids) != len(set(product_ids)):
            raise ValueError(
                "یک کالا نمی‌تواند بیشتر از یک بار "
                "در یک سفارش ثبت شود."
            )

        order_task = OrderTask.objects.create(
            task=task,
            warehouse=warehouse,

            product=None,
            quantity=None,
            completed_quantity=None,
            product_sale_price=None,

            title=task.title,
            description=task.description,
            case=task.case,
            department=task.department,
            current_step=task.current_step,
            created_by=task.created_by,
            note=note,
            file=file,
            status=OrderTask.Status.IN_PROGRESS,
        )

        OrderTaskItem.objects.bulk_create(
            [
                OrderTaskItem(
                    order_task=order_task,
                    product=item["product"],
                    quantity=item["quantity"],
                    completed_quantity=0,
                    status=OrderTaskItem.Status.PENDING,
                )
                for item in items
            ]
        )

        order_task.assigned_employee.set(
            task.assigned_employee.all()
        )

        OrderTaskDeadline.objects.create(
            order_task=order_task,
            started_at=started_at,
            deadline=deadline,
        )

        transaction.on_commit(
            lambda: OrderTaskService._send_creation_sms(
                order_task=order_task,
            )
        )

        return order_task

    @staticmethod
    @transaction.atomic
    def update(
        *,
        order_task,
        performed_by=None,
        status=None,
        completed_items=None,
        note=None,
        file=None,
    ):

        order_task = (
            OrderTask.objects
            .select_for_update()
            .get(pk=order_task.pk)
        )

        order_task = (
            OrderTask.objects
            .select_related(
                "warehouse",
                "task",
                "case",
                "case__customer",
                "department",
                "current_step",
                "created_by",
                "performed_by",
                "performed_by__employee",
                "performed_by__employee__user",
                "product",
            )
            .prefetch_related(
                "assigned_employee",
                "items__product",
            )
            .get(pk=order_task.pk)
        )

        new_performed_by = (
            performed_by
            if performed_by is not None
            else order_task.performed_by
        )

        if status is not None:

            if new_performed_by is None:
                raise ValueError(
                    "تا زمانی که انجام‌دهنده تسک مشخص نشده باشد، "
                    "امکان تغییر وضعیت تسک وجود ندارد."
                )

            if status not in OrderTask.Status.values:
                raise ValueError(
                    "وضعیت واردشده معتبر نیست."
                )

            if status in (
                OrderTask.Status.COMPLETED,
                OrderTask.Status.CANCELLED,
            ) and (
                not note or not note.strip()
            ):
                raise ValueError(
                    "هنگام تکمیل یا لغو تسک، "
                    "توضیحات الزامی است."
                )

        if status == OrderTask.Status.COMPLETED:

            if order_task.status == OrderTask.Status.COMPLETED:
                raise ValueError(
                    "این تسک قبلاً تکمیل شده است."
                )

            if not order_task.warehouse:
                raise ValueError(
                    "انبار تسک سفارش مشخص نشده است."
                )

            if not completed_items:
                raise ValueError(
                    "هنگام تکمیل سفارش، "
                    "لیست کالاهای ارسال‌شده الزامی است."
                )

            order_items = {
                item.product_id: item
                for item in order_task.items.all()
            }

            if not order_items:
                raise ValueError(
                    "این سفارش هیچ کالایی ندارد."
                )

            completed_map = {}

            for item in completed_items:

                product_id = item.get("product_id")
                quantity = item.get("quantity")

                if product_id in completed_map:
                    raise ValueError(
                        "یک کالا نمی‌تواند بیشتر از یک بار "
                        "در لیست ارسال ثبت شود."
                    )

                if quantity is None or quantity <= 0:
                    raise ValueError(
                        "تعداد ارسال‌شده باید بیشتر از صفر باشد."
                    )

                completed_map[product_id] = quantity

            for product_id in completed_map:

                if product_id not in order_items:
                    raise ValueError(
                        f"کالای {product_id} "
                        "در این سفارش وجود ندارد."
                    )

            for order_item in order_task.items.all():

                completed_quantity = completed_map.get(
                    order_item.product_id,
                    0,
                )

                if completed_quantity <= 0:

                    order_item.status = (
                        OrderTaskItem.Status.FAILED
                    )

                    order_item.error_message = (
                        "برای این کالا مقدار ارسال‌شده "
                        "ثبت نشده است."
                    )

                    order_item.completed_quantity = 0

                    order_item.save(
                        update_fields=[
                            "status",
                            "error_message",
                            "completed_quantity",
                            "updated_at",
                        ]
                    )

                    continue

                if completed_quantity > order_item.quantity:

                    order_item.status = (
                        OrderTaskItem.Status.FAILED
                    )

                    order_item.error_message = (
                        "تعداد ارسال‌شده نمی‌تواند "
                        "بیشتر از تعداد سفارش باشد."
                    )

                    order_item.completed_quantity = 0

                    order_item.save(
                        update_fields=[
                            "status",
                            "error_message",
                            "completed_quantity",
                            "updated_at",
                        ]
                    )

                    continue

                try:

                    with transaction.atomic():

                        stock_transaction = (
                            InventoryService.stock_out(
                                warehouse=order_task.warehouse,
                                product=order_item.product,
                                quantity=completed_quantity,
                                performed_by_id=(
                                    new_performed_by.id
                                ),
                                reason=(
                                    StockTransaction
                                    .StockOutReason
                                    .SALE
                                ),
                                note=note.strip(),
                            )
                        )

                        order_item.completed_quantity = (
                            completed_quantity
                        )

                        order_item.product_sale_price = (
                            order_item.product.sale_price
                        )

                        order_item.status = (
                            OrderTaskItem.Status.SUCCESS
                        )

                        order_item.error_message = None

                        order_item.stock_transaction = (
                            stock_transaction
                        )

                        order_item.save(
                            update_fields=[
                                "completed_quantity",
                                "product_sale_price",
                                "status",
                                "error_message",
                                "stock_transaction",
                                "updated_at",
                            ]
                        )

                except ValueError as exc:

                    order_item.status = (
                        OrderTaskItem.Status.FAILED
                    )

                    order_item.completed_quantity = 0

                    order_item.error_message = str(exc)

                    order_item.stock_transaction = None

                    order_item.product_sale_price = (
                        order_item.product.sale_price
                    )

                    order_item.save(
                        update_fields=[
                            "status",
                            "completed_quantity",
                            "error_message",
                            "stock_transaction",
                            "product_sale_price",
                            "updated_at",
                        ]
                    )

        elif status == OrderTask.Status.CANCELLED:

            if order_task.status == OrderTask.Status.COMPLETED:
                raise ValueError(
                    "تسک تکمیل شده را نمی‌توان لغو کرد."
                )

            for order_item in order_task.items.all():

                order_item.product_sale_price = (
                    order_item.product.sale_price
                )

                order_item.save(
                    update_fields=[
                        "product_sale_price",
                        "updated_at",
                    ]
                )

        if performed_by is not None:
            order_task.performed_by = performed_by

        if status is not None:
            order_task.status = status

        order_task.save(
            update_fields=[
                "performed_by",
                "status",
            ]
        )

        if status in (
            OrderTask.Status.COMPLETED,
            OrderTask.Status.CANCELLED,
        ):

            OrderTaskAttachment.objects.create(
                order_task=order_task,
                performed_by=new_performed_by,
                note=note.strip(),
                file=file,
            )

            OrderTaskDeadline.objects.filter(
                order_task=order_task
            ).delete()

            order_task = (
                OrderTask.objects
                .select_related(
                    "warehouse",
                    "task",
                    "case",
                    "case__customer",
                    "department",
                    "current_step",
                    "created_by",
                    "performed_by",
                    "performed_by__employee",
                    "performed_by__employee__user",
                    "product",
                )
                .prefetch_related(
                    "assigned_employee",
                    "items__product",
                    "items__stock_transaction",
                )
                .get(pk=order_task.pk)
            )

            OrderTaskService._create_archive(
                order_task
            )

        return order_task