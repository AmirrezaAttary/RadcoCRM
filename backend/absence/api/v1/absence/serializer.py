from rest_framework import serializers

from absence.models import (
    Absence,
    AbsenceAttachment,
)


def get_user_display_name(user):
    employee = getattr(
        user,
        "employee_profile",
        None,
    )

    if employee:
        return employee.user.profile.full_name

    return user.username


class AbsenceAttachmentListSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = AbsenceAttachment
        fields = [
            "id",
            "file",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class AbsenceAttachmentRetrieveSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = AbsenceAttachment
        fields = [
            "id",
            "file",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class AbsenceAttachmentCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = AbsenceAttachment
        fields = [
            "file",
        ]


class AbsenceAttachmentUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = AbsenceAttachment
        fields = [
            "file",
        ]


class AbsenceAttachmentPatchSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = AbsenceAttachment
        fields = [
            "file",
        ]



class AbsenceListSerializer(
    serializers.ModelSerializer
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    user_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Absence
        fields = [
            "id",
            "user",
            "user_name",
            "reviewed_by",
            "reviewed_by_name",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "reviewed_by",
            "reviewed_by_name",
            "status",
            "status_display",
            "active",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return get_user_display_name(obj.user)

    def get_reviewed_by_name(self, obj):
        if not obj.reviewed_by:
            return None

        return get_user_display_name(
            obj.reviewed_by
        )


class AbsenceRetrieveSerializer(
    serializers.ModelSerializer
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    user_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    attachments = AbsenceAttachmentRetrieveSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Absence
        fields = [
            "id",
            "user",
            "user_name",
            "reviewed_by",
            "reviewed_by_name",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "active",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "reviewed_by",
            "reviewed_by_name",
            "status",
            "status_display",
            "active",
            "attachments",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        return get_user_display_name(obj.user)

    def get_reviewed_by_name(self, obj):
        if not obj.reviewed_by:
            return None

        return get_user_display_name(
            obj.reviewed_by
        )


class AbsenceCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Absence
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if (
            start_date
            and end_date
            and end_date <= start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "زمان پایان مرخصی باید "
                        "بعد از زمان شروع باشد."
                    )
                }
            )

        return attrs
    

class AbsenceUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Absence
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date,
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date,
        )

        if end_date <= start_date:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "زمان پایان مرخصی باید "
                        "بعد از زمان شروع باشد."
                    )
                }
            )

        return attrs


class AbsencePatchSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Absence
        fields = [
            "title",
            "description",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date,
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date,
        )

        if end_date <= start_date:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "زمان پایان مرخصی باید "
                        "بعد از زمان شروع باشد."
                    )
                }
            )

        return attrs



class AbsenceApproveSerializer(
    serializers.Serializer
):
    pass


class AbsenceRejectSerializer(
    serializers.Serializer
):
    pass
