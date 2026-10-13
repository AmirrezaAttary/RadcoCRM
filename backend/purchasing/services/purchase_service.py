from django.db import transaction
from django.core.exceptions import ValidationError

from purchasing.models.purchase_task import (
    PurchaseTask,
    PurchaseTaskAttachment,
)
from purchasing.models.purchase_step import PurchaseProcessStep
from purchasing.models.purchase_employee import (
    PurchaseProcessEmployee,
)

from warehouse.models.warehouse_staff import WarehouseStaff

from notifications.sms import send_sms

from quality_control.services.quality_control import (
    QualityControlService,
)


class PurchaseService:

    @staticmethod
    def _send_purchase_task_sms(task, stock=None):

        warehouse = task.warehouse
        product = task.product

        purchase_employees = (
            PurchaseProcessEmployee.objects
            .select_related(
                "employee__user",
            )
            .filter(
                is_active=True,
                employee__is_active=True,
                employee__user__is_active=True,
            )
        )

        if warehouse:
            purchase_message = (
                f"تسک خرید جدید برای کالا «{product.name}» "
                f"در انبار «{warehouse.name}» ایجاد شد. "
                f"مقدار مورد نیاز خرید: {task.purchase_quantity}"
            )
        else:
            purchase_message = (
                f"تسک موجودی اولیه برای کالا «{product.name}» "
                f"ایجاد شد. "
                f"مقدار اولیه: {task.purchase_quantity}"
            )

        for purchase_employee in purchase_employees:

            phone_number = (
                purchase_employee.employee.user.phone_number
            )

            if phone_number:
                try:
                    send_sms(
                        number=phone_number,
                        message=purchase_message,
                    )
                except Exception:
                    pass

        if task.source != PurchaseTask.Source.SYSTEM:
            return

        if stock is None:
            return

        warehouse_staff = (
            WarehouseStaff.objects
            .select_related(
                "employee__user",
            )
            .filter(
                is_active=True,
                employee__is_active=True,
                employee__user__is_active=True,
            )
        )

        warehouse_message = (
            f"موجودی کالای «{product.name}» "
            f"در انبار «{warehouse.name}» "
            f"به کمتر از حداقل موجودی رسید. "
            f"موجودی فعلی: {stock.current_quantity}، "
            f"حداقل موجودی: {stock.minimum_stock}. "
            f"تسک خرید برای فرآیند خرید ایجاد شد."
        )

        for staff in warehouse_staff:

            phone_number = (
                staff.employee.user.phone_number
            )

            if phone_number:
                try:
                    send_sms(
                        number=phone_number,
                        message=warehouse_message,
                    )
                except Exception:
                    pass

    @staticmethod
    @transaction.atomic
    def create_purchase_task(product, stock):

        first_step = (
            PurchaseProcessStep.objects
            .filter(order=1)
            .first()
        )

        if not first_step:
            return None

        purchase_quantity = (
            stock.maximum_stock
            - stock.current_quantity
        )

        if purchase_quantity <= 0:
            return None

        purchase_task = PurchaseTask.objects.create(
            warehouse=stock.warehouse,
            product=product,
            process_step=first_step,
            minimum_stock=stock.minimum_stock,
            maximum_stock=stock.maximum_stock,
            quantity_after=stock.current_quantity,
            purchase_quantity=purchase_quantity,
            source=PurchaseTask.Source.SYSTEM,
            created_by=None,
            status=PurchaseTask.Status.PENDING,
        )

        PurchaseService._send_purchase_task_sms(
            task=purchase_task,
            stock=stock,
        )

        return purchase_task

    @staticmethod
    @transaction.atomic
    def create_manual_purchase_task(
        data,
        created_by,
    ):

        purchase_task = PurchaseTask.objects.create(
            warehouse=data["warehouse"],
            product=data["product"],
            process_step=data["process_step"],
            purchase_quantity=data["purchase_quantity"],
            source=PurchaseTask.Source.MANUAL,
            created_by=created_by,
            status=PurchaseTask.Status.PENDING,
        )

        PurchaseService._send_purchase_task_sms(
            task=purchase_task,
            stock=None,
        )

        return purchase_task

    @staticmethod
    @transaction.atomic
    def create_initial_purchase_task(
        product,
        quantity,
        created_by,
    ):

        first_step = (
            PurchaseProcessStep.objects
            .filter(order=1)
            .first()
        )

        if not first_step:
            raise ValidationError(
                "مرحله اول فرآیند خرید تعریف نشده است."
            )

        if quantity is None:
            raise ValidationError(
                "مقدار موجودی اولیه الزامی است."
            )

        if quantity <= 0:
            raise ValidationError(
                "مقدار موجودی اولیه باید بیشتر از صفر باشد."
            )

        purchase_task = PurchaseTask.objects.create(
            warehouse=None,
            product=product,
            process_step=first_step,
            minimum_stock=None,
            maximum_stock=None,
            quantity_after=None,
            purchase_quantity=quantity,
            source=PurchaseTask.Source.INITIAL,
            created_by=created_by,
            status=PurchaseTask.Status.PENDING,
        )

        PurchaseService._send_purchase_task_sms(
            task=purchase_task,
            stock=None,
        )

        return purchase_task

    @staticmethod
    def _create_quality_control(task):

        return QualityControlService.create_quality_control(
            purchase_task=task
        )

    @staticmethod
    @transaction.atomic
    def advance_task(
        task,
        employee,
        note=None,
        file=None,
    ):

        PurchaseTask.objects \
            .select_for_update() \
            .get(pk=task.pk)

        task = (
            PurchaseTask.objects
            .select_related(
                "process_step",
                "warehouse",
                "product",
            )
            .get(pk=task.pk)
        )

        if task.status in [
            PurchaseTask.Status.COMPLETED,
            PurchaseTask.Status.CANCELLED,
        ]:
            raise ValidationError(
                "این تسک به وضعیت نهایی رسیده و امکان حرکت "
                "در فرآیند خرید ندارد."
            )

        current_step = task.process_step

        next_step = (
            PurchaseProcessStep.objects
            .filter(
                order__gt=current_step.order
            )
            .order_by("order")
            .first()
        )

        if next_step:

            task.process_step = next_step

            if task.status == PurchaseTask.Status.PENDING:
                task.status = PurchaseTask.Status.IN_PROGRESS

            task.save(
                update_fields=[
                    "process_step",
                    "status",
                    "updated_at",
                ]
            )

            attachment = PurchaseTaskAttachment.objects.create(
                task=task,
                type=PurchaseTaskAttachment.Type.ADVANCE,
                process_step=next_step,
                note=note,
                file=file,
                created_by=employee,
            )

            return task, attachment

        task.status = PurchaseTask.Status.COMPLETED

        task.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        attachment = PurchaseTaskAttachment.objects.create(
            task=task,
            type=PurchaseTaskAttachment.Type.ADVANCE,
            process_step=current_step,
            note=note,
            file=file,
            created_by=employee,
        )

        PurchaseService._create_quality_control(task)

        return task, attachment

    @staticmethod
    @transaction.atomic
    def revert_task(
        task,
        employee,
        note=None,
        file=None,
    ):

        PurchaseTask.objects \
            .select_for_update() \
            .get(pk=task.pk)

        task = (
            PurchaseTask.objects
            .select_related(
                "process_step",
                "warehouse",
                "product",
            )
            .get(pk=task.pk)
        )

        if task.status in [
            PurchaseTask.Status.COMPLETED,
            PurchaseTask.Status.CANCELLED,
        ]:
            raise ValidationError(
                "این تسک به وضعیت نهایی رسیده و امکان بازگشت "
                "در فرآیند خرید ندارد."
            )

        current_step = task.process_step

        previous_step = (
            PurchaseProcessStep.objects
            .filter(
                order__lt=current_step.order
            )
            .order_by("-order")
            .first()
        )

        if not previous_step:
            raise ValidationError(
                "این تسک در اولین مرحله فرآیند قرار دارد "
                "و امکان بازگشت ندارد."
            )

        task.process_step = previous_step
        task.status = PurchaseTask.Status.IN_PROGRESS

        task.save(
            update_fields=[
                "process_step",
                "status",
                "updated_at",
            ]
        )

        attachment = PurchaseTaskAttachment.objects.create(
            task=task,
            type=PurchaseTaskAttachment.Type.REVERT,
            process_step=previous_step,
            note=note,
            file=file,
            created_by=employee,
        )

        return task, attachment

    @staticmethod
    @transaction.atomic
    def change_status(task, status):

        PurchaseTask.objects \
            .select_for_update() \
            .get(pk=task.pk)

        task = (
            PurchaseTask.objects
            .select_related(
                "process_step",
                "warehouse",
                "product",
            )
            .get(pk=task.pk)
        )

        if task.status in [
            PurchaseTask.Status.COMPLETED,
            PurchaseTask.Status.CANCELLED,
        ]:
            raise ValidationError(
                "وضعیت این تسک قبلاً نهایی شده و امکان تغییر "
                "آن وجود ندارد."
            )

        if status not in [
            PurchaseTask.Status.COMPLETED,
            PurchaseTask.Status.CANCELLED,
        ]:
            raise ValidationError(
                "فقط وضعیت Completed یا Cancelled "
                "قابل ثبت دستی است."
            )

        task.status = status

        task.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        if status == PurchaseTask.Status.COMPLETED:
            PurchaseService._create_quality_control(task)

        return task