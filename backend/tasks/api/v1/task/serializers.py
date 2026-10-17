from rest_framework import serializers

from tasks.models import Task, TaskStepLog, TaskStepDeadline
from accounts.models import Employee
from tasks.models.cases import Case

from ..task_attachment.serializers import TaskAttachmentSerializer


class TaskListSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    current_step_name = serializers.CharField(
        source="current_step.name",
        read_only=True,
    )

    assigned_employee_name = serializers.CharField(
        source="assigned_employee.full_name",
        read_only=True,
    )

    class Meta:
        model = Task

        fields = (
            "id",
            "title",
            "case",
            "department",
            "department_name",
            "current_step",
            "current_step_name",
            "assigned_employee",
            "assigned_employee_name",
            "status",
            "active",
            "created_at",
        )


class TaskCreateSerializer(serializers.ModelSerializer):

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
    )

    case = serializers.PrimaryKeyRelatedField(
        queryset=Case.objects.all(),
        required=False,
        allow_null=True,
    )

    assigned_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        required=True,
    )

    class Meta:
        model = Task

        fields = (
            "title",
            "description",
            "status",
            "case",
            "department",
            "assigned_employee",
            "files",
        )


class TaskDetailSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    current_step_name = serializers.CharField(
        source="current_step.name",
        read_only=True,
    )

    assigned_employee_name = serializers.CharField(
        source="assigned_employee.full_name",
        read_only=True,
    )

    attachments = TaskAttachmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Task

        fields = (
            "id",
            "title",
            "description",
            "case",
            "department",
            "department_name",
            "current_step",
            "current_step_name",
            "assigned_employee",
            "assigned_employee_name",
            "status",
            "active",
            "created_at",
            "completed_at",
            "updated_at",
            "attachments",
        )


class TaskActionSerializer(serializers.Serializer):

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    score = serializers.IntegerField(
        required=False,
        min_value=0,
        max_value=5,
        allow_null=True,
    )

    score_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class TaskAdvanceSerializer(TaskActionSerializer):

    # مسئول(های) مرحله‌ی بعد؛ می‌تواند خود کاربر هم باشد.
    # اگر مرحله‌ی فعلی آخرین مرحله باشد، نادیده گرفته می‌شود.
    next_assigned_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        many=True,
        required=False,
    )


class TaskReopenSerializer(serializers.Serializer):
    pass


class TaskStepLogSerializer(serializers.ModelSerializer):

    step_name = serializers.CharField(
        source="step.name",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    attachments = TaskAttachmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = TaskStepLog

        fields = (
            "id",
            "step",
            "step_name",
            "employee",
            "employee_name",
            "action",
            "note",
            "created_at",
            "attachments",
        )


class TaskUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task

        fields = (
            "title",
            "description",
            "assigned_employee",
        )


class TaskStepDeadlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskStepDeadline

        fields = [
            "id",
            "task",
            "department_step",
            "started_at",
            "deadline",
        ]

        read_only_fields = [
            "id",
            "task",
            "department_step",
        ]


class TaskStepDeadlinePatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskStepDeadline

        fields = [
            "started_at",
            "deadline",
        ]


class TaskStepDeadlineUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskStepDeadline

        fields = [
            "started_at",
            "deadline",
        ]


class CompleteTaskSerializer(serializers.Serializer):

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    score = serializers.IntegerField(
        required=False,
        min_value=0,
        max_value=5,
        allow_null=True,
    )

    score_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class TaskDeactivateSerializer(serializers.Serializer):
    pass


class TaskActivateSerializer(serializers.Serializer):
    pass