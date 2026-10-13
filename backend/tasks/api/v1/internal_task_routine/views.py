from rest_framework import (
    generics,
    serializers,
)
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
)

from tasks.models.internal_task import (
    InternalTaskRoutine,
)
from tasks.api.v1.internal_task_routine.serializers import (
    InternalTaskRoutineSerializer,
    InternalTaskRoutineCreateSerializer,
    InternalTaskRoutinePatchSerializer,
)
from tasks.services.internal_task_routine import (
    create_internal_task_routine,
    update_internal_task_routine,
    delete_internal_task_routine,
)
from access.internal_task import (
    InternalTaskAccess,
)


class InternalTaskRoutineListView(
    generics.ListAPIView
):

    serializer_class = (
        InternalTaskRoutineSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        task_queryset = (
            InternalTaskAccess.get_queryset(
                self.request.user
            )
        )

        return (
            InternalTaskRoutine.objects
            .filter(
                task__in=task_queryset,
            )
            .select_related(
                "task",
            )
        )


class InternalTaskRoutineCreateView(
    generics.CreateAPIView
):

    serializer_class = (
        InternalTaskRoutineCreateSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(
        self,
        serializer,
    ):

        task = serializer.validated_data[
            "task"
        ]

        InternalTaskAccess.can_modify(
            self.request.user,
            task,
        )

        try:

            routine = (
                create_internal_task_routine(
                    task=task,
                    start_at=(
                        serializer.validated_data[
                            "start_at"
                        ]
                    ),
                    interval_days=(
                        serializer.validated_data[
                            "interval_days"
                        ]
                    ),
                )
            )

        except ValueError as exc:

            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            )

        serializer.instance = routine



class InternalTaskRoutineRetrieveView(
    generics.RetrieveAPIView
):

    serializer_class = (
        InternalTaskRoutineSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        task_queryset = (
            InternalTaskAccess.get_queryset(
                self.request.user
            )
        )

        return (
            InternalTaskRoutine.objects
            .filter(
                task__in=task_queryset,
            )
            .select_related(
                "task",
            )
        )


class InternalTaskRoutinePatchView(
    generics.UpdateAPIView
):

    serializer_class = (
        InternalTaskRoutinePatchSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    http_method_names = [
        "patch",
        "options",
    ]

    def get_queryset(self):

        task_queryset = (
            InternalTaskAccess.get_queryset(
                self.request.user
            )
        )

        return (
            InternalTaskRoutine.objects
            .filter(
                task__in=task_queryset,
            )
            .select_related(
                "task",
            )
        )

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):

        instance = self.get_object()

        InternalTaskAccess.can_modify(
            request.user,
            instance.task,
        )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:

            routine = (
                update_internal_task_routine(
                    routine=instance,
                    **serializer.validated_data,
                )
            )

        except ValueError as exc:

            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            )

        return Response(
            InternalTaskRoutineSerializer(
                routine,
                context={
                    "request": request,
                },
            ).data
        )


class InternalTaskRoutineDestroyView(
    generics.DestroyAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        task_queryset = (
            InternalTaskAccess.get_queryset(
                self.request.user
            )
        )

        return (
            InternalTaskRoutine.objects
            .filter(
                task__in=task_queryset,
            )
            .select_related(
                "task",
            )
        )

    def perform_destroy(
        self,
        instance,
    ):

        InternalTaskAccess.can_modify(
            self.request.user,
            instance.task,
        )

        delete_internal_task_routine(
            routine=instance,
        )