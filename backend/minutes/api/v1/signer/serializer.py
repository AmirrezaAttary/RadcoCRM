import base64
import binascii

from rest_framework import serializers

from minutes.models import Meeting, Signer

SIGNATURE_PREFIX = "data:image/png;base64,"
SIGNATURE_MAX_LENGTH = 500_000
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _check_identity(attrs, instance=None):
    """
    هر امضاکننده یا user دارد یا full_name
    """
    user = attrs.get("user", getattr(instance, "user", None))
    full_name = attrs.get("full_name", getattr(instance, "full_name", ""))

    if user is None and not (full_name or "").strip():
        raise serializers.ValidationError(
            "برای امضاکننده‌ی بیرونی، نام و نام خانوادگی الزامی است."
        )


class SignerListSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_external = serializers.BooleanField(read_only=True)
    is_signed = serializers.BooleanField(read_only=True)
    sign_token = serializers.SerializerMethodField()

    class Meta:
        model = Signer
        fields = (
            "id",
            "meeting",
            "user",
            "username",
            "full_name",
            "display_name",
            "phone_number",
            "is_external",
            "role_title",
            "order",
            "is_signed",
            "signed_at",
            "sign_token",
        )

    def get_username(self, obj) -> str | None:
        return obj.user.username if obj.user_id else None

    def get_sign_token(self, obj) -> str | None:
        """
        توکن لینک امضا فقط برای افراد بیرونی و فقط برای ایجادکننده/ادمین
        (وگرنه هر امضاکننده می‌توانست به جای دیگری امضا کند)
        """
        request = self.context.get("request")

        if request is None or not obj.is_external:
            return None

        user = request.user
        if user.is_staff or obj.meeting.created_by_id == user.id:
            return str(obj.token)

        return None


class SignerDetailSerializer(SignerListSerializer):

    class Meta(SignerListSerializer.Meta):
        fields = SignerListSerializer.Meta.fields + (
            "signature_image",
            "signed_ip",
            "signed_hash",
        )


class SignerInlineSerializer(serializers.ModelSerializer):
    """
    برای افزودن امضاکننده‌ها هنگام ساخت صورت جلسه
    """

    class Meta:
        model = Signer
        fields = (
            "user",
            "full_name",
            "phone_number",
            "role_title",
            "order",
        )

    def validate_user(self, user):
        if user is not None and not user.is_active:
            raise serializers.ValidationError("این کاربر غیرفعال است.")
        return user

    def validate(self, attrs):
        _check_identity(attrs)
        return attrs


class SignerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Signer
        fields = (
            "id",
            "meeting",
            "user",
            "full_name",
            "phone_number",
            "role_title",
            "order",
        )
        read_only_fields = ("id",)

    def validate_user(self, user):
        if user is not None and not user.is_active:
            raise serializers.ValidationError("این کاربر غیرفعال است.")
        return user

    def validate(self, attrs):
        _check_identity(attrs)
        return attrs

    def validate_meeting(self, meeting):
        request = self.context["request"]

        if not (
            request.user.is_staff
            or meeting.created_by_id == request.user.id
        ):
            raise serializers.ValidationError(
                "شما به این صورت جلسه دسترسی ندارید."
            )

        if not meeting.is_draft:
            raise serializers.ValidationError(
                "فقط صورت جلسه‌ی پیش‌نویس قابل تغییر است."
            )

        return meeting


class SignerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Signer
        fields = (
            "full_name",
            "phone_number",
            "role_title",
            "order",
        )

    def validate(self, attrs):
        _check_identity(attrs, self.instance)

        if not self.instance.meeting.is_draft:
            raise serializers.ValidationError(
                "فقط صورت جلسه‌ی پیش‌نویس قابل تغییر است."
            )
        return attrs


class SignerSignSerializer(serializers.Serializer):

    signature_image = serializers.CharField(
        write_only=True,
    )

    def validate_signature_image(self, value):

        if not value.startswith(SIGNATURE_PREFIX):
            raise serializers.ValidationError(
                "امضا باید تصویر PNG به صورت data URL باشد."
            )

        if len(value) > SIGNATURE_MAX_LENGTH:
            raise serializers.ValidationError("حجم تصویر امضا زیاد است.")

        try:
            raw = base64.b64decode(
                value[len(SIGNATURE_PREFIX):],
                validate=True,
            )
        except (binascii.Error, ValueError):
            raise serializers.ValidationError("تصویر امضا معتبر نیست.")

        if not raw.startswith(PNG_MAGIC):
            raise serializers.ValidationError("تصویر امضا معتبر نیست.")

        return value



class PublicMeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "held_at",
            "location",
            "body",
            "status",
        )


class PublicSignerSerializer(serializers.ModelSerializer):
    """
    چیزی که شخص بیرونی با لینک امضا می‌بیند؛
    بدون توکن و تصویر امضای بقیه
    """

    meeting = PublicMeetingSerializer(read_only=True)
    display_name = serializers.CharField(read_only=True)
    is_signed = serializers.BooleanField(read_only=True)
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Signer
        fields = (
            "display_name",
            "role_title",
            "is_signed",
            "signed_at",
            "meeting",
            "participants",
        )

    def get_participants(self, obj) -> list:
        return [
            {
                "display_name": s.display_name,
                "role_title": s.role_title,
                "is_signed": s.is_signed,
            }
            for s in obj.meeting.signers.select_related("user__employee_profile")
        ]
