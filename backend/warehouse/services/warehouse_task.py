from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from warehouse.models.warehouse_process import InventoryStock
from warehouse.models.warehouse_task import WarehouseTask
from warehouse.models.warehouse_task_archive import WarehouseTaskArchive
from warehouse.services.warehouse_process import InventoryService
from purchasing.models.purchase_task import PurchaseTask


class WarehouseTaskService:

    @staticmethod
    def _create_archive(
        task,
        quantity_before=None,
        quantity_after=None,
    ):
        purchase_task = task.purchase_task
        quality_control = task.quality_control
        product = task.product
        warehouse = task.warehouse
        warehouse_staff = task.assigned_to

        stock = None

        if warehouse and product:
            stock = (
                InventoryStock.objects
                .filter(
                    warehouse=warehouse,
                    product=product,
                )
                .first()
            )

        created_by = (
            purchase_task.created_by
            if purchase_task
            else None
        )

        created_by_employee = None

        if created_by:
            created_by_employee = getattr(
                created_by,
                "employee_profile",
                None,
            )

        created_by_full_name = None

        if created_by:
            created_by_full_name = getattr(
                created_by.profile,
                "full_name",
                None,
            )

        if not created_by_full_name and created_by_employee:
            created_by_full_name = getattr(
                created_by_employee.user.profile,
                "full_name",
                None,
            )

        WarehouseTaskArchive.objects.create(
            warehouse_task=task,

            purchase_task_id=(
                purchase_task.id
                if purchase_task
                else None
            ),

            purchase_task_title=(
                purchase_task.product.name
                if (
                    purchase_task
                    and purchase_task.product
                )
                else None
            ),

            purchase_task_source=(
                purchase_task.source
                if purchase_task
                else None
            ),

            purchase_task_created_by_id=(
                created_by.id
                if created_by
                else None
            ),

            purchase_task_created_by_employee_id=(
                created_by_employee.id
                if created_by_employee
                else None
            ),

            purchase_task_created_by_full_name=(
                created_by_full_name
            ),

            quality_control_id=(
                quality_control.id
                if quality_control
                else None
            ),

            quality_control_title=(
                quality_control.purchase_task.product.name
                if (
                    quality_control
                    and quality_control.purchase_task
                    and quality_control.purchase_task.product
                )
                else None
            ),

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

            product_id=(
                product.id
                if product
                else None
            ),

            product_name=(
                product.name
                if product
                else None
            ),

            minimum_stock=(
                stock.minimum_stock
                if stock
                else None
            ),

            maximum_stock=(
                stock.maximum_stock
                if stock
                else None
            ),

            expected_quantity=task.expected_quantity,

            received_quantity=task.received_quantity,

            quantity_before=quantity_before,

            quantity_after=quantity_after,

            status=task.status,

            assigned_to_id=(
                warehouse_staff.id
                if warehouse_staff
                else None
            ),

            assigned_to_employee_id=(
                warehouse_staff.employee_id
                if warehouse_staff
                else None
            ),

            assigned_to_full_name=(
                warehouse_staff.employee.user.profile.full_name
                if (
                    warehouse_staff
                    and warehouse_staff.employee
                )
                else None
            ),

            note=task.note or "",

            file=task.file,

            task_created_at=task.created_at,

            task_updated_at=task.updated_at,

            completed_at=task.completed_at,
        )

    @staticmethod
    @transaction.atomic
    def activate(task):

        task = (
            WarehouseTask.objects
            .select_for_update()
            .get(pk=task.pk)
        )

        if task.active:
            raise ValidationError(
                "این تسک از قبل فعال است."
            )

        task.active = True

        task.save(
            update_fields=[
                "active",
                "updated_at",
            ]
        )

        return task

    @staticmethod
    @transaction.atomic
    def deactivate(task):

        task = (
            WarehouseTask.objects
            .select_for_update()
            .get(pk=task.pk)
        )

        if not task.active:
            raise ValidationError(
                "این تسک از قبل غیرفعال است."
            )

        task.active = False

        task.save(
            update_fields=[
                "active",
                "updated_at",
            ]
        )

        return task

    @staticmethod
    @transaction.atomic
    def cancel_task(
        task,
        note=None,
    ):

        task = (
            WarehouseTask.objects
            .select_for_update(of=("self",))
            .select_related(
                "purchase_task",
                "purchase_task__warehouse",
                "purchase_task__product",
                "purchase_task__created_by",
                "purchase_task__created_by__profile",
                "purchase_task__created_by__employee_profile",
                "purchase_task__created_by__employee_profile__user",
                "purchase_task__created_by__employee_profile__user__profile",
                "quality_control",
                "product",
                "warehouse",
                "assigned_to",
                "assigned_to__employee",
                "assigned_to__employee__user",
                "assigned_to__employee__user__profile",
            )
            .get(pk=task.pk)
        )

        if not task.active:
            raise ValidationError(
                "این تسک غیرفعال است و امکان لغو آن وجود ندارد."
            )

        if task.status == WarehouseTask.Status.COMPLETED:
            raise ValidationError(
                "تسک تکمیل شده را نمی‌توان لغو کرد."
            )

        if task.status == WarehouseTask.Status.CANCELLED:
            raise ValidationError(
                "این تسک قبلاً لغو شده است."
            )

        if task.status not in (
            WarehouseTask.Status.PENDING,
            WarehouseTask.Status.IN_PROGRESS,
        ):
            raise ValidationError(
                "این تسک در وضعیت قابل لغو نیست."
            )

        task.status = WarehouseTask.Status.CANCELLED

        if note is not None:
            task.note = note

        task.save(
            update_fields=[
                "status",
                "note",
                "updated_at",
            ]
        )

        WarehouseTaskService._create_archive(task)

        return task

    @staticmethod
    @transaction.atomic
    def restore_cancelled_task(task):

        task = (
            WarehouseTask.objects
            .select_for_update()
            .get(pk=task.pk)
        )

        if not task.active:
            raise ValidationError(
                "این تسک غیرفعال است و امکان بازگردانی آن وجود ندارد."
            )

        if task.status != WarehouseTask.Status.CANCELLED:
            raise ValidationError(
                "فقط تسک لغو شده را می‌توان "
                "به حالت در انتظار برگرداند."
            )

        task.status = WarehouseTask.Status.PENDING
        task.completed_at = None

        task.save(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        return task

    @staticmethod
    @transaction.atomic
    def complete_task(
        task,
        warehouse_staff,
        received_quantity,
        note=None,
        file=None,
    ):

        task = (
            WarehouseTask.objects
            .select_for_update(of=("self",))
            .select_related(
                "warehouse",
                "product",
                "quality_control",
                "purchase_task",
                "purchase_task__warehouse",
                "purchase_task__product",
                "purchase_task__created_by",
                "purchase_task__created_by__profile",
                "purchase_task__created_by__employee_profile",
                "purchase_task__created_by__employee_profile__user",
                "purchase_task__created_by__employee_profile__user__profile",
                "assigned_to",
                "assigned_to__employee",
                "assigned_to__employee__user",
                "assigned_to__employee__user__profile",
            )
            .get(pk=task.pk)
        )

        if not task.active:
            raise ValidationError(
                "این تسک غیرفعال است و امکان تکمیل آن وجود ندارد."
            )

        if task.status == WarehouseTask.Status.COMPLETED:
            raise ValidationError(
                "این تسک قبلاً تکمیل شده است."
            )

        if task.status != WarehouseTask.Status.PENDING:
            raise ValidationError(
                "این تسک در وضعیت قابل تکمیل نیست."
            )

        if not task.quality_control:
            raise ValidationError(
                "کنترل کیفیت برای این تسک مشخص نشده است."
            )

        if (
            task.quality_control.status
            != task.quality_control.Status.APPROVED
        ):
            raise ValidationError(
                "این کالا توسط کنترل کیفیت تایید نشده است."
            )

        if not warehouse_staff:
            raise ValidationError(
                "انباردار مشخص نشده است."
            )

        if not warehouse_staff.is_active:
            raise ValidationError(
                "انباردار انتخاب شده فعال نیست."
            )

        if received_quantity is None:
            raise ValidationError(
                "مقدار دریافت شده الزامی است."
            )

        if received_quantity <= 0:
            raise ValidationError(
                "مقدار دریافت شده باید بیشتر از صفر باشد."
            )

        if task.received_quantity is not None:
            raise ValidationError(
                "مقدار دریافت شده این تسک قبلاً ثبت شده است."
            )

        if not task.warehouse:
            raise ValidationError(
                "انبار این تسک مشخص نشده است."
            )

        if not task.product:
            raise ValidationError(
                "کالای این تسک مشخص نشده است."
            )

        if (
            task.purchase_task
            and task.purchase_task.warehouse_id
            != task.warehouse_id
        ):
            raise ValidationError(
                "انبار تسک انبار با انبار تسک خرید "
                "مطابقت ندارد."
            )

        if (
            task.purchase_task
            and task.purchase_task.product_id
            != task.product_id
        ):
            raise ValidationError(
                "کالای تسک انبار با کالای تسک خرید "
                "مطابقت ندارد."
            )

        try:
            stock = (
                InventoryStock.objects
                .select_for_update()
                .get(
                    warehouse=task.warehouse,
                    product=task.product,
                )
            )

        except InventoryStock.DoesNotExist:
            raise ValidationError(
                f"موجودی {task.product.name} در انبار "
                f"{task.warehouse.name} هنوز ثبت نشده است."
            )

        if stock.maximum_stock <= 0:
            raise ValidationError(
                f"حداکثر موجودی برای کالای "
                f"{task.product.name} در انبار "
                f"{task.warehouse.name} تنظیم نشده است."
            )

        if stock.minimum_stock < 0:
            raise ValidationError(
                f"حداقل موجودی برای کالای "
                f"{task.product.name} در انبار "
                f"{task.warehouse.name} معتبر نیست."
            )

        if stock.minimum_stock > stock.maximum_stock:
            raise ValidationError(
                "حداقل موجودی نمی‌تواند بیشتر از "
                "حداکثر موجودی باشد."
            )

        current_quantity = stock.current_quantity

        final_quantity = (
            current_quantity
            + received_quantity
        )

        if final_quantity > stock.maximum_stock:
            available_capacity = (
                stock.maximum_stock
                - current_quantity
            )

            raise ValidationError(
                f"ظرفیت انبار برای این کالا کافی نیست. "
                f"حداکثر موجودی: {stock.maximum_stock}، "
                f"موجودی فعلی: {current_quantity}، "
                f"حداکثر مقدار قابل دریافت: "
                f"{max(available_capacity, 0)}"
            )

        transaction_obj = InventoryService.stock_in(
            warehouse=task.warehouse,
            product=task.product,
            quantity=received_quantity,
            performed_by_id=warehouse_staff.pk,
            note=note or "",
        )

        task.assigned_to = warehouse_staff
        task.received_quantity = received_quantity
        task.note = note
        task.file = file
        task.status = WarehouseTask.Status.COMPLETED
        task.completed_at = timezone.now()

        task.save(
            update_fields=[
                "assigned_to",
                "received_quantity",
                "note",
                "file",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        task = (
            WarehouseTask.objects
            .select_related(
                "warehouse",
                "purchase_task",
                "purchase_task__warehouse",
                "purchase_task__product",
                "purchase_task__created_by",
                "purchase_task__created_by__profile",
                "purchase_task__created_by__employee_profile",
                "purchase_task__created_by__employee_profile__user",
                "purchase_task__created_by__employee_profile__user__profile",
                "quality_control",
                "product",
                "assigned_to",
                "assigned_to__employee",
                "assigned_to__employee__user",
                "assigned_to__employee__user__profile",
            )
            .get(pk=task.pk)
        )

        WarehouseTaskService._create_archive(
            task,
            quantity_before=transaction_obj.quantity_before,
            quantity_after=transaction_obj.quantity_after,
        )

        return task, transaction_obj

    @staticmethod
    @transaction.atomic
    def complete_initial_task(
        task,
        warehouse,
        warehouse_staff,
        received_quantity,
        minimum_stock,
        maximum_stock,
        note=None,
        file=None,
    ):

        task = (
            WarehouseTask.objects
            .select_for_update(of=("self",))
            .select_related(
                "warehouse",
                "product",
                "quality_control",
                "purchase_task",
                "purchase_task__warehouse",
                "purchase_task__product",
                "purchase_task__created_by",
                "purchase_task__created_by__profile",
                "purchase_task__created_by__employee_profile",
                "purchase_task__created_by__employee_profile__user",
                "purchase_task__created_by__employee_profile__user__profile",
                "assigned_to",
                "assigned_to__employee",
                "assigned_to__employee__user",
                "assigned_to__employee__user__profile",
            )
            .get(pk=task.pk)
        )

        if not task.active:
            raise ValidationError(
                "این تسک غیرفعال است و امکان تکمیل آن وجود ندارد."
            )

        if task.status == WarehouseTask.Status.COMPLETED:
            raise ValidationError(
                "این تسک قبلاً تکمیل شده است."
            )

        if task.status != WarehouseTask.Status.PENDING:
            raise ValidationError(
                "این تسک در وضعیت قابل تکمیل نیست."
            )

        if not task.purchase_task:
            raise ValidationError(
                "تسک خرید برای این تسک انبار مشخص نشده است."
            )

        if task.purchase_task.source != PurchaseTask.Source.INITIAL:
            raise ValidationError(
                "این endpoint فقط برای تسک‌های موجودی اولیه است."
            )

        if not task.quality_control:
            raise ValidationError(
                "کنترل کیفیت برای این تسک مشخص نشده است."
            )

        if (
            task.quality_control.status
            != task.quality_control.Status.APPROVED
        ):
            raise ValidationError(
                "این کالا توسط کنترل کیفیت تایید نشده است."
            )

        if not task.product:
            raise ValidationError(
                "کالای این تسک مشخص نشده است."
            )

        if not warehouse:
            raise ValidationError(
                "انبار الزامی است."
            )

        if not warehouse_staff:
            raise ValidationError(
                "انباردار مشخص نشده است."
            )

        if not warehouse_staff.is_active:
            raise ValidationError(
                "انباردار انتخاب شده فعال نیست."
            )

        if received_quantity is None:
            raise ValidationError(
                "مقدار موجودی اولیه الزامی است."
            )

        if received_quantity <= 0:
            raise ValidationError(
                "مقدار موجودی اولیه باید بیشتر از صفر باشد."
            )

        if minimum_stock is None:
            raise ValidationError(
                "حداقل موجودی الزامی است."
            )

        if minimum_stock < 0:
            raise ValidationError(
                "حداقل موجودی نمی‌تواند منفی باشد."
            )

        if maximum_stock is None:
            raise ValidationError(
                "حداکثر موجودی الزامی است."
            )

        if maximum_stock <= 0:
            raise ValidationError(
                "حداکثر موجودی باید بیشتر از صفر باشد."
            )

        if minimum_stock > maximum_stock:
            raise ValidationError(
                "حداقل موجودی نمی‌تواند بیشتر از "
                "حداکثر موجودی باشد."
            )

        if (
            task.purchase_task.product_id
            != task.product_id
        ):
            raise ValidationError(
                "کالای تسک انبار با کالای تسک خرید "
                "مطابقت ندارد."
            )

        if InventoryStock.objects.filter(
            warehouse=warehouse,
            product=task.product,
        ).exists():
            raise ValidationError(
                f"موجودی اول دوره برای {task.product.name} "
                f"در انبار {warehouse.name} قبلاً ثبت شده است."
            )

        stock = InventoryService.add_initial_stock(
            warehouse=warehouse,
            product=task.product,
            quantity=received_quantity,
            minimum_stock=minimum_stock,
            maximum_stock=maximum_stock,
            performed_by_id=warehouse_staff.pk,
        )

        task.warehouse = warehouse
        task.assigned_to = warehouse_staff
        task.received_quantity = received_quantity
        task.note = note
        task.file = file
        task.status = WarehouseTask.Status.COMPLETED
        task.completed_at = timezone.now()

        task.save(
            update_fields=[
                "warehouse",
                "assigned_to",
                "received_quantity",
                "note",
                "file",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        task = (
            WarehouseTask.objects
            .select_related(
                "warehouse",
                "purchase_task",
                "purchase_task__warehouse",
                "purchase_task__product",
                "purchase_task__created_by",
                "purchase_task__created_by__profile",
                "purchase_task__created_by__employee_profile",
                "purchase_task__created_by__employee_profile__user",
                "purchase_task__created_by__employee_profile__user__profile",
                "quality_control",
                "product",
                "assigned_to",
                "assigned_to__employee",
                "assigned_to__employee__user",
                "assigned_to__employee__user__profile",
            )
            .get(pk=task.pk)
        )

        WarehouseTaskService._create_archive(
            task,
            quantity_before=0,
            quantity_after=stock.current_quantity,
        )

        return task, stock