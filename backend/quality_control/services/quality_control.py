from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from quality_control.models.quality_control import QualityControl
from quality_control.models.employee import QualityControlEmployee

from purchasing.models.purchase_task import PurchaseTask
from purchasing.models.purchase_step import PurchaseProcessStep

from warehouse.models.warehouse_task import WarehouseTask
from warehouse.models.warehouse_staff import WarehouseStaff

from notifications.sms import send_sms


class QualityControlService:

    @staticmethod
    def _send_quality_control_sms(quality_control):

        purchase_task = quality_control.purchase_task

        product = purchase_task.product
        warehouse = purchase_task.warehouse

        quality_control_employees = (
            QualityControlEmployee.objects
            .select_related("user")
            .filter(
                is_active=True,
                user__is_active=True,
            )
        )

        if warehouse:
            message = (
                f"تسک خرید «{product.name}» "
                f"از انبار «{warehouse.name}» "
                "وارد مرحله کنترل کیفیت شد. "
                "لطفاً جهت بررسی تسک به سامانه مراجعه کنید."
            )
        else:
            message = (
                f"تسک موجودی اولیه کالای «{product.name}» "
                "وارد مرحله کنترل کیفیت شد. "
                "لطفاً جهت بررسی تسک به سامانه مراجعه کنید."
            )

        for employee in quality_control_employees:

            phone_number = employee.user.phone_number

            if not phone_number:
                continue

            try:
                send_sms(
                    number=phone_number,
                    message=message,
                )
            except Exception:
                pass

    @staticmethod
    def _send_warehouse_task_sms(warehouse_task):

        warehouse_staffs = (
            WarehouseStaff.objects
            .select_related(
                "employee",
                "employee__user",
            )
            .filter(
                is_active=True,
                employee__is_active=True,
                employee__user__is_active=True,
            )
        )

        if warehouse_task.warehouse:
            message = (
                f"تسک دریافت کالای «{warehouse_task.product.name}» "
                f"در انبار «{warehouse_task.warehouse.name}» "
                f"ایجاد شد. مقدار مورد انتظار: "
                f"{warehouse_task.expected_quantity}. "
                "لطفاً جهت انجام تسک به سامانه مراجعه کنید."
            )
        else:
            message = (
                f"تسک ثبت موجودی اولیه کالای "
                f"«{warehouse_task.product.name}» ایجاد شد. "
                f"مقدار مورد انتظار: "
                f"{warehouse_task.expected_quantity}. "
                "لطفاً انبار و مشخصات موجودی اولیه را در سامانه ثبت کنید."
            )

        for warehouse_staff in warehouse_staffs:

            phone_number = (
                warehouse_staff.employee.user.phone_number
            )

            if not phone_number:
                continue

            try:
                send_sms(
                    number=phone_number,
                    message=message,
                )
            except Exception:
                pass

    @staticmethod
    @transaction.atomic
    def create_quality_control(
        purchase_task,
    ):

        if not purchase_task:
            raise ValidationError(
                "تسک خرید مشخص نشده است."
            )

        PurchaseTask.objects \
            .select_for_update() \
            .get(pk=purchase_task.pk)

        purchase_task = (
            PurchaseTask.objects
            .select_related(
                "warehouse",
                "product",
                "process_step",
            )
            .get(pk=purchase_task.pk)
        )

        if purchase_task.status != PurchaseTask.Status.COMPLETED:
            raise ValidationError(
                "فقط برای تسک خرید تکمیل شده می‌توان کنترل کیفیت ایجاد کرد."
            )

        pending_qc_exists = (
            QualityControl.objects
            .filter(
                purchase_task=purchase_task,
                status=QualityControl.Status.PENDING,
            )
            .exists()
        )

        if pending_qc_exists:
            raise ValidationError(
                "این تسک در حال حاضر یک کنترل کیفیت در انتظار بررسی دارد."
            )

        quality_control = QualityControl.objects.create(
            purchase_task=purchase_task,
            status=QualityControl.Status.PENDING,
        )

        transaction.on_commit(
            lambda: QualityControlService._send_quality_control_sms(
                quality_control=quality_control,
            )
        )

        return quality_control

    @staticmethod
    @transaction.atomic
    def approve(
        quality_control,
        checked_by,
        note=None,
        file=None,
    ):

        QualityControl.objects \
            .select_for_update() \
            .get(pk=quality_control.pk)

        quality_control = (
            QualityControl.objects
            .select_related(
                "purchase_task",
                "purchase_task__product",
                "purchase_task__warehouse",
            )
            .get(pk=quality_control.pk)
        )

        if quality_control.status != QualityControl.Status.PENDING:
            raise ValidationError(
                "این کنترل کیفیت قبلاً بررسی شده است."
            )

        if not checked_by:
            raise ValidationError(
                "کاربر بررسی‌کننده مشخص نشده است."
            )

        purchase_task = quality_control.purchase_task

        if not purchase_task:
            raise ValidationError(
                "تسک خرید برای کنترل کیفیت مشخص نشده است."
            )

        if purchase_task.status != PurchaseTask.Status.COMPLETED:
            raise ValidationError(
                "فقط کنترل کیفیت مربوط به تسک خرید تکمیل شده "
                "قابل تایید است."
            )

        if not purchase_task.product:
            raise ValidationError(
                "کالای تسک خرید مشخص نشده است."
            )

        if hasattr(quality_control, "warehouse_task"):
            raise ValidationError(
                "برای این کنترل کیفیت قبلاً تسک انبار ایجاد شده است."
            )

        quality_control.status = QualityControl.Status.APPROVED
        quality_control.checked_by = checked_by
        quality_control.note = note
        quality_control.file = file
        quality_control.checked_at = timezone.now()

        quality_control.save(
            update_fields=[
                "status",
                "checked_by",
                "note",
                "file",
                "checked_at",
            ]
        )

        warehouse_task = WarehouseTask.objects.create(
            purchase_task=purchase_task,
            warehouse=purchase_task.warehouse,
            quality_control=quality_control,
            product=purchase_task.product,
            expected_quantity=purchase_task.purchase_quantity,
            status=WarehouseTask.Status.PENDING,
        )

        transaction.on_commit(
            lambda: QualityControlService._send_warehouse_task_sms(
                warehouse_task=warehouse_task,
            )
        )

        return quality_control, warehouse_task

    @staticmethod
    @transaction.atomic
    def reject(
        quality_control,
        checked_by,
        note=None,
        file=None,
    ):

        quality_control = (
            QualityControl.objects
            .select_for_update()
            .select_related(
                "purchase_task",
                "purchase_task__process_step",
                "purchase_task__warehouse",
                "purchase_task__product",
            )
            .get(pk=quality_control.pk)
        )

        if quality_control.status != QualityControl.Status.PENDING:
            raise ValidationError(
                "این کنترل کیفیت قبلاً بررسی شده است."
            )

        if not checked_by:
            raise ValidationError(
                "کاربر بررسی‌کننده مشخص نشده است."
            )

        first_step = (
            PurchaseProcessStep.objects
            .order_by("order")
            .first()
        )

        if not first_step:
            raise ValidationError(
                "هیچ مرحله‌ای برای فرآیند خرید تعریف نشده است."
            )

        quality_control.status = QualityControl.Status.REJECTED
        quality_control.checked_by = checked_by
        quality_control.note = note
        quality_control.file = file
        quality_control.checked_at = timezone.now()

        quality_control.save(
            update_fields=[
                "status",
                "checked_by",
                "note",
                "file",
                "checked_at",
            ]
        )

        purchase_task = quality_control.purchase_task

        purchase_task.process_step = first_step
        purchase_task.status = PurchaseTask.Status.IN_PROGRESS

        purchase_task.save(
            update_fields=[
                "process_step",
                "status",
                "updated_at",
            ]
        )

        return quality_control