import base64
import binascii

from rest_framework import serializers

from hr.models import ContractSignature

SIGNATURE_PREFIX = "data:image/png;base64,"
SIGNATURE_MAX_LENGTH = 500_000
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class SignatureListSerializer(serializers.ModelSerializer):
    """
    بدون تصویر امضا (برای لیست‌ها)
    """

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    contract_title = serializers.CharField(
        source="contract.title",
        read_only=True,
    )
    contract_status = serializers.CharField(
        source="contract.status",
        read_only=True,
    )
    is_signed = serializers.BooleanField(read_only=True)
    registered_by_username = serializers.CharField(
        source="registered_by.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = ContractSignature
        fields = (
            "id",
            "contract",
            "contract_title",
            "contract_status",
            "employee",
            "employee_name",
            "is_signed",
            "signed_at",
            "method",
            "registered_by",
            "registered_by_username",
        )


class SignatureDetailSerializer(SignatureListSerializer):
    """
    همراه با تصویر امضا؛ فقط برای ادمین و خودِ امضاکننده
    """

    class Meta(SignatureListSerializer.Meta):
        fields = SignatureListSerializer.Meta.fields + (
            "signature_image",
            "signed_ip",
            "signed_hash",
        )


class SignatureSignSerializer(serializers.Serializer):

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
