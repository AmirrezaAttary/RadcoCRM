from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from drf_spectacular.utils import extend_schema

from access.task import TaskAccess
from access.permissions import TaskPermission, TaskModifyPermission
from access.permissions import WarehousePermission

from accounts.models.employee import Employee

from tasks.services import tasks as services
from tasks.services.tasks import (
    get_task_step_deadline,
    set_task_step_deadline,
    complete_task,
)
from tasks.exceptions import TaskServiceError
from tasks.models import Task, TaskStepLog
from .serializers import (
    TaskListSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskActionSerializer,
    TaskAdvanceSerializer,
    TaskStepLogSerializer,
    TaskUpdateSerializer,
    TaskStepDeadlineSerializer,
    TaskStepDeadlineSerializer,
    TaskStepDeadlineUpdateSerializer,
    TaskStepDeadlinePatchSerializer,
    TaskReopenSerializer,
    TaskTransferSerializer,
    CompleteTaskSerializer,
    TaskDeactivateSerializer,
    TaskActivateSerializer,
)


class TaskListApi(generics.ListAPIView):

    serializer_class = TaskListSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    def get_queryset(self):
        return TaskAccess.get_queryset(
            self.request.user,
        ).filter(status=Task.Status.IN_PROGRESS)




class TaskCreateApi(generics.CreateAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskCreateSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        try:
            task = services.create_task(
                title=serializer.validated_data["title"],
                description=serializer.validated_data.get("description", ""),
                case=serializer.validated_data.get("case", None),
                department=serializer.validated_data["department"],
                assigned_employee=serializer.validated_data["assigned_employee"],
                created_by=self.request.user,
                files=serializer.validated_data.get("files", []),
                current_step=serializer.validated_data.get("current_step"),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        serializer.instance = task


class TaskDetailApi(generics.RetrieveAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string",
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5,
                    "nullable": True,
                },
                "score_reason": {
                    "type": "string",
                },
                "next_assigned_employee": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": (
                        "شناسه‌ی کارمند(های) مسئول مرحله‌ی بعد. "
                        "برای انتقال به مرحله‌ی بعد الزامی است و می‌تواند "
                        "خود کاربر باشد."
                    ),
                },
            },
        },
    },
    responses=TaskDetailSerializer,
)
class TaskAdvanceApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskAdvanceSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند مسئول تسک می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = services.advance_step(
                task=task,
                employee=employee,
                note=serializer.validated_data.get(
                    "note",
                    "",
                ),
                files=serializer.validated_data.get(
                    "files",
                    [],
                ),
                score=serializer.validated_data.get(
                    "score"
                ),
                score_reason=serializer.validated_data.get(
                    "score_reason",
                    "",
                ),
                next_assigned_employee=serializer.validated_data.get(
                    "next_assigned_employee",
                    [],
                ),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        return Response(
            TaskDetailSerializer(task).data,
        )

@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "note": {"type": "string"},
                "files": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                },
            },
        },
    },
    responses=TaskDetailSerializer,
)
class TaskRevertApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskActionSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند مسئول تسک می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            task = services.revert_step(
                task=task,
                employee=employee,
                note=serializer.validated_data["note"],
                files=serializer.validated_data.get("files", []),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        return Response(
            TaskDetailSerializer(task).data,
        )


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "required": ["department"],
            "properties": {
                "department": {
                    "type": "integer",
                    "description": (
                        "شناسه‌ی دپارتمان مقصد. تسک به اولین مرحله‌ی "
                        "این دپارتمان می‌رود و به مدیر آن اختصاص داده می‌شود."
                    ),
                },
                "note": {"type": "string"},
                "files": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                },
            },
        },
    },
    responses=TaskDetailSerializer,
)
class TaskTransferApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskTransferSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند مسئول تسک می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = services.transfer_task_to_department(
                task=task,
                employee=employee,
                department=serializer.validated_data["department"],
                note=serializer.validated_data.get("note", ""),
                files=serializer.validated_data.get("files", []),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        return Response(
            TaskDetailSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


class TaskStepLogListApi(generics.ListAPIView):

    serializer_class = TaskStepLogSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        task = get_object_or_404(
            Task,
            pk=self.kwargs["task_id"],
        )

        self.check_object_permissions(self.request, task)

        return TaskStepLog.objects.filter(task=task)


class TaskUpdateApi(generics.UpdateAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskUpdateSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )


class TaskDeleteApi(generics.DestroyAPIView):

    permission_classes = (
        IsAuthenticated,
        TaskModifyPermission,
    )

    def get_queryset(self):
        return TaskAccess.get_queryset(self.request.user)


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "note": {"type": "string"},
                "files": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                },
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5,
                    "nullable": True,
                },
                "score_reason": {
                    "type": "string",
                },
            },
        },
    },
    responses=TaskDetailSerializer,
)
class TaskCancelApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskActionSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = services.cancel_task(
                task=task,
                cancelled_by=employee,
                score=serializer.validated_data.get(
                    "score"
                ),
                score_reason=serializer.validated_data.get(
                    "score_reason",
                    "",
                ),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        return Response(
            TaskDetailSerializer(task).data
        )

class TaskMarkAsSoldApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskActionSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند مسئول تسک می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            task = services.sell_task(
                task=task,
                employee=employee,
                score=serializer.validated_data.get(
                    "score"
                ),
                score_reason=serializer.validated_data.get(
                    "score_reason",
                    "",
                ),
            )

        except TaskServiceError as error:
            raise ValidationError(str(error))

        return Response(
            TaskDetailSerializer(task).data
        )

class TaskStepDeadlineDetailView(generics.GenericAPIView):
    serializer_class = TaskStepDeadlineSerializer
    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    def get(self, request, task_id, department_step_id):
        obj = get_task_step_deadline(
            task_id=task_id,
            department_step_id=department_step_id,
        )

        serializer = self.get_serializer(obj)

        return Response(serializer.data)

class TaskStepDeadlineUpdateView(generics.GenericAPIView):
    serializer_class = TaskStepDeadlineUpdateSerializer
    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    def put(self, request, task_id, department_step_id):
        obj = get_task_step_deadline(
            task_id=task_id,
            department_step_id=department_step_id,
        )

        serializer = self.get_serializer(
            obj,
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            TaskStepDeadlineSerializer(obj).data
        )

class TaskStepDeadlineDeleteView(generics.GenericAPIView):
    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    def delete(self, request, task_id, department_step_id):
        obj = get_task_step_deadline(
            task_id=task_id,
            department_step_id=department_step_id,
        )

        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class TaskStepDeadlinePatchView(generics.GenericAPIView):
    serializer_class = TaskStepDeadlinePatchSerializer
    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    def patch(self, request, task_id, department_step_id):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        obj = set_task_step_deadline(
            task_id=task_id,
            department_step_id=department_step_id,
            started_at=serializer.validated_data.get("started_at"),
            deadline=serializer.validated_data.get("deadline"),
        )

        return Response(
            TaskStepDeadlineSerializer(obj).data
        )


class TaskReopenApi(
    generics.GenericAPIView
):

    serializer_class = TaskReopenSerializer

    # دسترسی به تسک‌های بسته‌شده با TaskAccess (مسئول/سازنده) محدود است،
    # اما مدیر دپارتمان باید بتواند بدون مسئول بودن، تسک را برگرداند.
    # بررسی «مدیر بودن» داخل سرویس reopen_task انجام می‌شود.
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        try:
            employee = self.request.user.employee_profile
        except ObjectDoesNotExist:
            return Task.objects.none()

        return (
            Task.objects
            .filter(
                department__employee_memberships__employee=employee,
            )
            .select_related(
                "case",
                "department",
                "current_step",
                "created_by",
            )
            .distinct()
        )

    def post(self, request, *args, **kwargs):

        # -----------------------------------------------------
        # Get Task
        # -----------------------------------------------------

        task = self.get_object()

        try:
            employee = request.user.employee_profile
        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط مدیر دپارتمان می‌تواند این عملیات را انجام دهد."
            )

        # -----------------------------------------------------
        # Validate Request
        # -----------------------------------------------------

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        # -----------------------------------------------------
        # Reopen
        # -----------------------------------------------------

        try:

            task = services.reopen_task(
                task=task,
                employee=employee,
                current_step=serializer.validated_data["current_step"],
                assigned_employee=serializer.validated_data["assigned_employee"],
            )

        except TaskServiceError as error:

            raise ValidationError(
                str(error)
            )

        # -----------------------------------------------------
        # Response
        # -----------------------------------------------------

        return Response(
            TaskDetailSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string",
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5,
                    "nullable": True,
                },
                "score_reason": {
                    "type": "string",
                },
            },
        },
    },
    responses=TaskDetailSerializer,
)
class CompleteTaskView(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = CompleteTaskSerializer

    permission_classes = (
        IsAuthenticated,
        TaskPermission,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request, *args, **kwargs):

        task = self.get_object()

        try:
            employee = request.user.employee_profile

        except ObjectDoesNotExist:
            raise PermissionDenied(
                "فقط کارمند مسئول تسک می‌تواند این عملیات را انجام دهد."
            )

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:

            task = services.complete_task(
                task=task,
                employee=employee,
                note=serializer.validated_data.get(
                    "note",
                    "",
                ),
                files=serializer.validated_data.get(
                    "files",
                    [],
                ),
                score=serializer.validated_data.get(
                    "score",
                ),
                score_reason=serializer.validated_data.get(
                    "score_reason",
                    "",
                ),
            )

        except TaskServiceError as error:

            raise ValidationError(
                str(error)
            )

        return Response(
            TaskDetailSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )
        
@extend_schema(
    request=TaskDeactivateSerializer,
    responses=TaskDetailSerializer,
)
class TaskDeactivateApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskDeactivateSerializer

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            task = services.deactivate_task(
                task=task,
            )

        except TaskServiceError as error:
            raise ValidationError(
                str(error)
            )

        return Response(
            TaskDetailSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=TaskActivateSerializer,
    responses=TaskDetailSerializer,
)
class TaskActivateApi(generics.GenericAPIView):

    queryset = Task.objects.all()

    serializer_class = TaskActivateSerializer

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):

        task = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            task = services.activate_task(
                task=task,
            )

        except TaskServiceError as error:
            raise ValidationError(
                str(error)
            )

        return Response(
            TaskDetailSerializer(
                task,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )