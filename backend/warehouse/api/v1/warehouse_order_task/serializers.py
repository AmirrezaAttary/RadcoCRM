import json

from rest_framework import serializers

from tasks.models.tasks import Task

from warehouse.models.warehouse_order_task import (
    OrderTask,
    OrderTaskItem,
    OrderTaskDeadline,
    OrderTaskAttachment,
)

from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.models.product import Product
from warehouse.models.warehouse import Warehouse


class OrderTaskDeadlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderTaskDeadline
        fields = [
            "id",
            "order_task",
            "started_at",
            "deadline",
        ]


class OrderTaskEmployeeSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    full_name = serializers.CharField(
        read_only=True,
    )


class OrderTaskAttachmentNestedSerializer(
    serializers.ModelSerializer
):

    performed_by = serializers.SerializerMethodField()

    class Meta:
        model = OrderTaskAttachment
        fields = [
            "id",
            "performed_by",
            "note",
            "file",
            "created_at",
        ]

    def get_performed_by(self, obj):

        if not obj.performed_by:
            return None

        if not obj.performed_by.employee:
            return None

        return {
            "id": obj.performed_by_id,
            "employee_id": obj.performed_by.employee_id,
            "full_name": obj.performed_by.employee.full_name,
        }


class OrderTaskItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    stock_transaction_id = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = OrderTaskItem

        fields = [
            "id",
            "product",
            "product_name",

            "quantity",
            "completed_quantity",

            "product_sale_price",

            "status",
            "status_display",
            "error_message",

            "stock_transaction_id",

            "created_at",
            "updated_at",
        ]


class OrderTaskSerializer(serializers.ModelSerializer):

    warehouse_name = serializers.CharField(
        source="warehouse.name",
        read_only=True,
    )

    warehouse_code = serializers.CharField(
        source="warehouse.code",
        read_only=True,
    )

    case = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()

    assigned_employee = OrderTaskEmployeeSerializer(
        many=True,
        read_only=True,
    )

    created_by = serializers.SerializerMethodField()
    performed_by = serializers.SerializerMethodField()

    deadline = OrderTaskDeadlineSerializer(
        read_only=True,
    )

    attachments = OrderTaskAttachmentNestedSerializer(
        many=True,
        read_only=True,
    )

    items = OrderTaskItemSerializer(
        many=True,
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = OrderTask

        fields = [
            "id",

            "task",

            "warehouse",
            "warehouse_name",
            "warehouse_code",

            "items",

            "title",
            "description",

            "case",
            "customer",
            "department",
            "current_step",

            "assigned_employee",

            "created_by",

            "note",
            "file",

            "performed_by",

            "status",
            "status_display",

            "deadline",
            "attachments",

            "created_at",
        ]

    def get_case(self, obj):

        if not obj.case:
            return None

        return {
            "id": obj.case_id,
            "title": obj.case.title,
        }

    def get_customer(self, obj):

        if not obj.case or not obj.case.customer:
            return None

        return {
            "id": obj.case.customer_id,
            "full_name": obj.case.customer.full_name,
        }

    def get_department(self, obj):

        if not obj.department:
            return None

        return {
            "id": obj.department_id,
            "name": obj.department.name,
        }

    def get_current_step(self, obj):

        if not obj.current_step:
            return None

        return {
            "id": obj.current_step_id,
            "name": obj.current_step.name,
        }

    def get_created_by(self, obj):

        if not obj.created_by:
            return None

        return {
            "id": obj.created_by_id,
            "username": obj.created_by.username,
        }

    def get_performed_by(self, obj):

        if not obj.performed_by:
            return None

        if not obj.performed_by.employee:
            return None

        return {
            "id": obj.performed_by_id,
            "employee_id": obj.performed_by.employee_id,
            "full_name": obj.performed_by.employee.full_name,
        }


class OrderTaskCreateItemSerializer(serializers.Serializer):

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )

    quantity = serializers.FloatField(
        min_value=0.0001,
    )


class OrderTaskCreateSerializer(serializers.Serializer):

    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="task",
    )

    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.filter(
            is_active=True
        ),
        source="warehouse",
    )

    items = serializers.CharField(
        required=True,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    started_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    deadline = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    def validate_items(self, value):

        if not isinstance(value, str):
            raise serializers.ValidationError(
                "items باید به صورت JSON ارسال شود."
            )

        try:
            items = json.loads(value)

        except json.JSONDecodeError:

            raise serializers.ValidationError(
                "فرمت items صحیح نیست. "
                "باید یک JSON معتبر باشد."
            )

        if not isinstance(items, list):

            raise serializers.ValidationError(
                "items باید یک آرایه JSON باشد."
            )

        if not items:

            raise serializers.ValidationError(
                "حداقل یک کالا برای سفارش الزامی است."
            )

        item_serializer = OrderTaskCreateItemSerializer(
            data=items,
            many=True,
        )

        item_serializer.is_valid(
            raise_exception=True
        )

        validated_items = (
            item_serializer.validated_data
        )

        product_ids = [
            item["product"].id
            for item in validated_items
        ]

        if len(product_ids) != len(set(product_ids)):

            raise serializers.ValidationError(
                "یک کالا نمی‌تواند بیشتر از یک بار "
                "در یک سفارش ثبت شود."
            )

        return validated_items


class OrderTaskCompletedItemSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    quantity = serializers.FloatField(
        min_value=0.0001,
    )


class OrderTaskUpdateSerializer(serializers.Serializer):

    performed_by = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseStaff.objects.filter(
            is_active=True
        ),
        required=False,
        allow_null=True,
    )

    status = serializers.ChoiceField(
        choices=OrderTask.Status.choices,
        required=False,
    )

    completed_items = serializers.CharField(
        required=False,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    def validate_completed_items(self, value):

        if not isinstance(value, str):
            raise serializers.ValidationError(
                "completed_items باید به صورت JSON ارسال شود."
            )

        try:
            items = json.loads(value)

        except json.JSONDecodeError:

            raise serializers.ValidationError(
                "فرمت completed_items صحیح نیست. "
                "باید یک JSON معتبر باشد."
            )

        if not isinstance(items, list):

            raise serializers.ValidationError(
                "completed_items باید یک آرایه JSON باشد."
            )

        if not items:

            raise serializers.ValidationError(
                "حداقل یک کالای ارسال‌شده باید ثبت شود."
            )

        item_serializer = OrderTaskCompletedItemSerializer(
            data=items,
            many=True,
        )

        item_serializer.is_valid(
            raise_exception=True
        )

        validated_items = (
            item_serializer.validated_data
        )

        product_ids = [
            item["product_id"]
            for item in validated_items
        ]

        if len(product_ids) != len(set(product_ids)):

            raise serializers.ValidationError(
                "یک کالا نمی‌تواند بیشتر از یک بار "
                "در لیست ارسال ثبت شود."
            )

        return validated_items

    def validate(self, attrs):

        status = attrs.get("status")

        staff = attrs.get("performed_by")

        if staff is None and status is not None:
            staff = self.instance.performed_by

        if (
            staff is not None
            and self.instance.warehouse_id
            and not staff.can_access_warehouse(
                self.instance.warehouse_id
            )
        ):
            raise serializers.ValidationError({
                "performed_by": (
                    "این انباردار به انبار این تسک دسترسی ندارد."
                )
            })

        if status in [
            OrderTask.Status.COMPLETED,
            OrderTask.Status.CANCELLED,
        ]:

            note = attrs.get("note")

            if not note or not note.strip():

                raise serializers.ValidationError({
                    "note": (
                        "هنگام تکمیل یا لغو تسک، "
                        "توضیحات الزامی است."
                    )
                })

        if status == OrderTask.Status.COMPLETED:

            if "completed_items" not in attrs:

                raise serializers.ValidationError({
                    "completed_items": (
                        "هنگام تکمیل تسک، "
                        "لیست کالاهای ارسال‌شده الزامی است."
                    )
                })

            if not attrs["completed_items"]:

                raise serializers.ValidationError({
                    "completed_items": (
                        "حداقل یک کالای ارسال‌شده "
                        "باید ثبت شود."
                    )
                })

        return attrs


class OrderTaskAttachmentListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrderTaskAttachment

        fields = [
            "id",
            "order_task",
            "performed_by",
            "note",
            "file",
            "created_at",
        ]


class OrderTaskAttachmentCreateSerializer(
    serializers.ModelSerializer
):

    order_task = serializers.PrimaryKeyRelatedField(
        queryset=OrderTask.objects.all(),
    )

    performed_by = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseStaff.objects.filter(
            is_active=True
        ),
    )

    note = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = OrderTaskAttachment

        fields = [
            "order_task",
            "performed_by",
            "note",
            "file",
        ]

    def validate_note(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "توضیحات الزامی است."
            )

        return value

    def validate(self, attrs):

        order_task = attrs["order_task"]
        staff = attrs["performed_by"]

        if (
            order_task.warehouse_id
            and not staff.can_access_warehouse(
                order_task.warehouse_id
            )
        ):
            raise serializers.ValidationError({
                "performed_by": (
                    "این انباردار به انبار این تسک دسترسی ندارد."
                )
            })

        return attrs


class OrderTaskAttachmentDetailSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = OrderTaskAttachment

        fields = [
            "id",
            "order_task",
            "performed_by",
            "note",
            "file",
            "created_at",
        ]


class OrderTaskAttachmentUpdateSerializer(
    serializers.ModelSerializer
):

    performed_by = serializers.PrimaryKeyRelatedField(
        queryset=WarehouseStaff.objects.filter(
            is_active=True
        ),
        required=False,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=False,
    )

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = OrderTaskAttachment

        fields = [
            "performed_by",
            "note",
            "file",
        ]

    def validate_note(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "توضیحات الزامی است."
            )

        return value

    def validate(self, attrs):

        staff = attrs.get("performed_by")

        if (
            staff is not None
            and self.instance.order_task.warehouse_id
            and not staff.can_access_warehouse(
                self.instance.order_task.warehouse_id
            )
        ):
            raise serializers.ValidationError({
                "performed_by": (
                    "این انباردار به انبار این تسک دسترسی ندارد."
                )
            })

        return attrs
