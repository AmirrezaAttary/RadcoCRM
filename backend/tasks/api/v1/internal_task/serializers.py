from rest_framework import serializers

from accounts.models import User

from tasks.models.internal_task import (
    InternalTask,
    InternalTaskDeadline,
)

from notifications.sms import send_sms

from tasks.models.internal_task_attachment import (
    InternalTaskAttachment,
)


class UserBriefSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "full_name",
        ]

    def get_full_name(self, obj):

        profile = getattr(
            obj,
            "profile",
            None,
        )

        if profile:
            return profile.full_name

        return ""


class InternalTaskDeadlineSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskDeadline

        fields = [
            "id",
            "started_at",
            "deadline",
        ]

        read_only_fields = [
            "id",
        ]


class InternalTaskDeadlinePatchSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskDeadline

        fields = [
            "started_at",
            "deadline",
        ]


class InternalTaskDeadlineUpdateSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = InternalTaskDeadline

        fields = [
            "started_at",
            "deadline",
        ]


class InternalTaskAttachmentSerializer(
    serializers.ModelSerializer
):

    uploaded_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = InternalTaskAttachment

        fields = [
            "id",
            "file",
            "original_file_name",
            "note",
            "uploaded_by",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "original_file_name",
            "uploaded_by",
            "created_at",
        ]


class InternalTaskSerializer(
    serializers.ModelSerializer
):

    assigned_to = UserBriefSerializer(
        many=True,
        read_only=True,
    )

    deadline = InternalTaskDeadlineSerializer(
        read_only=True,
    )

    created_by = serializers.StringRelatedField(
        read_only=True,
    )

    attachments = InternalTaskAttachmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = InternalTask

        fields = [
            "id",
            "title",
            "description",
            "status",
            "active",
            "assigned_to",
            "deadline",
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
            "attachments",
        ]


class InternalTaskWriteSerializer(
    serializers.ModelSerializer
):

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
    )

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = InternalTask

        fields = [
            "id",
            "title",
            "description",
            "status",
            "assigned_to",
            "created_by",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_by",
        ]

    def create(self, validated_data):

        assigned_to = validated_data.pop(
            "assigned_to",
            [],
        )

        task = InternalTask.objects.create(
            **validated_data
        )

        task.assigned_to.set(
            assigned_to
        )

        message = (
            f"تسک «{task.title}» به شما اختصاص داده شد."
        )

        for user in assigned_to:

            if user.phone_number:

                send_sms(
                    number=user.phone_number,
                    message=message,
                )

        return task

    def update(
        self,
        instance,
        validated_data,
    ):

        assigned_to = validated_data.pop(
            "assigned_to",
            None,
        )

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value,
            )

        instance.save()

        if assigned_to is not None:

            instance.assigned_to.set(
                assigned_to
            )

        return instance


class InternalTaskCompleteSerializer(
    serializers.Serializer
):

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class InternalTaskCancelSerializer(
    serializers.Serializer
):

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class InternalTaskReopenSerializer(
    serializers.Serializer
):
    pass


class InternalTaskActivateSerializer(
    serializers.Serializer
):
    pass


class InternalTaskDeactivateSerializer(
    serializers.Serializer
):
    pass
