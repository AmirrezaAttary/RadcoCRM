from rest_framework import serializers

from tasks.models.internal_task import (
    InternalTask,
    InternalTaskRoutine,
)


class InternalTaskRoutineSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskRoutine

        fields = [
            "id",
            "task",
            "start_at",
            "interval_days",
            "last_run_at",
            "next_run_at",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "last_run_at",
            "next_run_at",
            "is_active",
            "created_at",
            "updated_at",
        ]


class InternalTaskRoutineCreateSerializer(
    serializers.ModelSerializer
):

    task = serializers.PrimaryKeyRelatedField(
        queryset=InternalTask.objects.all(),
    )

    class Meta:
        model = InternalTaskRoutine

        fields = [
            "task",
            "start_at",
            "interval_days",
        ]

    def validate_interval_days(
        self,
        value,
    ):

        if value <= 0:

            raise serializers.ValidationError(
                "فاصله تکرار باید بیشتر از صفر باشد."
            )

        return value


class InternalTaskRoutinePatchSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskRoutine

        fields = [
            "start_at",
            "interval_days",
            "is_active",
        ]

    def validate_interval_days(
        self,
        value,
    ):

        if value <= 0:

            raise serializers.ValidationError(
                "فاصله تکرار باید بیشتر از صفر باشد."
            )

        return value