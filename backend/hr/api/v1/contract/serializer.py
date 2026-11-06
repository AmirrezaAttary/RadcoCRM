from rest_framework import serializers

from hr.models import Contract

from ..permissions import is_admin
from ..signature.serializer import (
    SignatureDetailSerializer,
    SignatureListSerializer,
)


class ContractListSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    signatures_count = serializers.IntegerField(read_only=True)
    signed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "title",
            "department",
            "department_name",
            "status",
            "created_by",
            "created_by_username",
            "signatures_count",
            "signed_count",
            "sent_at",
            "created_at",
        )


class ContractDetailSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )
    signatures = serializers.SerializerMethodField()
    will_sign = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = (
            "id",
            "title",
            "department",
            "department_name",
            "body",
            "status",
            "content_hash",
            "created_by",
            "created_by_username",
            "signatures",
            "will_sign",
            "sent_at",
            "created_at",
            "updated_at",
        )

    def get_signatures(self, obj) -> list:
        """
        تصویر امضا فقط برای ادمین؛ کارمند فقط وضعیت امضاها را می‌بیند
        """
        request = self.context.get("request")
        admin = request is not None and is_admin(request.user)

        serializer_class = (
            SignatureDetailSerializer if admin else SignatureListSerializer
        )

        return serializer_class(
            obj.signatures.select_related(
                "employee",
                "contract",
                "registered_by",
            ),
            many=True,
        ).data

    def get_will_sign(self, obj) -> list:
        """
        فقط در پیش‌نویس: کارمندانی که با ارسال، باید امضا کنند
        """
        if not obj.is_draft:
            return []

        return [
            {"id": e.id, "full_name": e.full_name}
            for e in obj.get_signing_employees()
        ]


class ContractCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = (
            "id",
            "title",
            "department",
            "body",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        return Contract.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )


class ContractUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = (
            "title",
            "department",
            "body",
        )

    def validate(self, attrs):
        if not self.instance.is_draft:
            raise serializers.ValidationError(
                "بعد از ارسال برای امضا، متن قرارداد قابل ویرایش نیست."
            )
        return attrs
