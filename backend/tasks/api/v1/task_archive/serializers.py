from rest_framework import serializers

from tasks.models.task_archive import TaskArchive

class TaskArchiveListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskArchive
        fields = [
            "id",
            "task_id",
            "title",
            "status",

            "case_id",
            "case_title",

            "customer_id",
            "customer_full_name",

            "department_id",
            "department_name",

            "created_by_id",
            "created_by_username",
            "created_by_full_name",

            "final_action_by_id",
            "final_action_by_username",
            "final_action_by_full_name",

            "task_created_at",
            "completed_at",
            "archived_at",
        ]

class TaskArchiveDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskArchive
        fields = "__all__"