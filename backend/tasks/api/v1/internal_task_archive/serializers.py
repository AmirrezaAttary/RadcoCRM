from rest_framework import serializers

from tasks.models.internal_task_archive import (
    InternalTaskArchive
)


class InternalTaskArchiveListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskArchive

        fields = [
            "id",
            "task_id",
            "title",
            "status",
            "created_by_id",
            "created_by_username",
            "created_by_full_name",
            "final_action_by_id",
            "final_action_by_username",
            "final_action_by_full_name",
            "task_created_at",
            "task_updated_at",
            "completed_at",
            "archived_at",
        ]


class InternalTaskArchiveDetailSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskArchive

        fields = [
            "id",
            "task_id",
            "title",
            "description",
            "status",
            "task_created_at",
            "task_updated_at",
            "completed_at",
            "archived_at",
            "assigned_employees_snapshot",
            "deadline_snapshot",
            "attachments_snapshot",
            "created_by_id",        
            "created_by_username",
            "created_by_full_name",
            "final_action_by_id",
            "final_action_by_username",
            "final_action_by_full_name",
        ]