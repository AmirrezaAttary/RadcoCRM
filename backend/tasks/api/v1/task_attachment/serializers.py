from rest_framework import serializers

from tasks.models import TaskAttachment


class TaskAttachmentSerializer(serializers.ModelSerializer):

    uploaded_by_username = serializers.CharField(
        source="uploaded_by.username",
        read_only=True,
    )

    class Meta:
        model = TaskAttachment

        fields = (
            "id",
            "file",
            "original_file_name",
            "uploaded_by",
            "uploaded_by_username",
            "created_at",
        )

        read_only_fields = ("uploaded_by",)


class TaskAttachmentUploadSerializer(serializers.Serializer):

    files = serializers.ListField(
        child=serializers.FileField(),
    )