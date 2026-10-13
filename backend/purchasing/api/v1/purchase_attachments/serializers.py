from rest_framework import serializers

from purchasing.models.purchase_task import (
    PurchaseTaskAttachment,
)


class PurchaseTaskAttachmentListSerializer(serializers.ModelSerializer):

    type_display = serializers.CharField(
        source="get_type_display",
        read_only=True,
    )

    process_step_order = serializers.IntegerField(
        source="process_step.order",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.employee.full_name",
        read_only=True,
    )

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "id",
            "task",
            "type",
            "type_display",
            "process_step",
            "process_step_order",
            "note",
            "file",
            "file_url",
            "created_by",
            "created_by_name",
            "created_at",
        ]

    def get_file_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url


class PurchaseTaskAttachmentCreateSerializer(serializers.ModelSerializer):

    type = serializers.ChoiceField(
        choices=PurchaseTaskAttachment.Type.choices
    )

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "task",
            "type",
            "process_step",
            "note",
            "file",
            "created_by",
        ]

    def validate(self, attrs):

        attachment_type = attrs.get("type")
        process_step = attrs.get("process_step")

        if attachment_type == PurchaseTaskAttachment.Type.TASK:
            if process_step is not None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست نوع تسک، مرحله فرآیند نباید مشخص شود."
                })

        elif attachment_type in [
            PurchaseTaskAttachment.Type.ADVANCE,
            PurchaseTaskAttachment.Type.REVERT,
        ]:
            if process_step is None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست Advance یا Revert، مرحله فرآیند الزامی است."
                })

        return attrs

    def create(self, validated_data):
        return PurchaseTaskAttachment.objects.create(
            **validated_data
        )


class PurchaseTaskAttachmentDetailSerializer(serializers.ModelSerializer):

    type_display = serializers.CharField(
        source="get_type_display",
        read_only=True,
    )

    process_step_order = serializers.IntegerField(
        source="process_step.order",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.employee.full_name",
        read_only=True,
    )

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "id",
            "task",
            "type",
            "type_display",
            "process_step",
            "process_step_order",
            "note",
            "file",
            "file_url",
            "created_by",
            "created_by_name",
            "created_at",
        ]

        read_only_fields = fields

    def get_file_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.file.url)

        return obj.file.url


class PurchaseTaskAttachmentUpdateSerializer(serializers.ModelSerializer):

    type = serializers.ChoiceField(
        choices=PurchaseTaskAttachment.Type.choices,
    )

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "task",
            "type",
            "process_step",
            "note",
            "file",
        ]

    def validate(self, attrs):

        attachment_type = attrs.get("type")
        process_step = attrs.get("process_step")

        if attachment_type == PurchaseTaskAttachment.Type.TASK:
            if process_step is not None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست نوع تسک، مرحله فرآیند نباید مشخص شود."
                })

        elif attachment_type in [
            PurchaseTaskAttachment.Type.ADVANCE,
            PurchaseTaskAttachment.Type.REVERT,
        ]:
            if process_step is None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست Advance یا Revert، مرحله فرآیند الزامی است."
                })

        return attrs


class PurchaseTaskAttachmentPartialUpdateSerializer(
    serializers.ModelSerializer
):

    type = serializers.ChoiceField(
        choices=PurchaseTaskAttachment.Type.choices,
        required=False,
    )

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "task",
            "type",
            "process_step",
            "note",
            "file",
        ]

    def validate(self, attrs):

        attachment_type = attrs.get(
            "type",
            getattr(self.instance, "type", None)
        )

        process_step = attrs.get(
            "process_step",
            getattr(self.instance, "process_step", None)
        )

        if attachment_type == PurchaseTaskAttachment.Type.TASK:
            if process_step is not None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست نوع تسک، مرحله فرآیند نباید مشخص شود."
                })

        elif attachment_type in [
            PurchaseTaskAttachment.Type.ADVANCE,
            PurchaseTaskAttachment.Type.REVERT,
        ]:
            if process_step is None:
                raise serializers.ValidationError({
                    "process_step":
                        "برای پیوست Advance یا Revert، مرحله فرآیند الزامی است."
                })

        return attrs


class PurchaseTaskAttachmentDeleteSerializer(serializers.ModelSerializer):

    type_display = serializers.CharField(
        source="get_type_display",
        read_only=True,
    )

    process_step_order = serializers.IntegerField(
        source="process_step.order",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PurchaseTaskAttachment

        fields = [
            "id",
            "task",
            "type",
            "type_display",
            "process_step",
            "process_step_order",
            "note",
            "file",
            "created_by",
            "created_at",
        ]

        read_only_fields = fields