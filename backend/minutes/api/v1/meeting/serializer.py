from django.db import transaction

from rest_framework import serializers

from minutes.models import Meeting, Signer

from ..signer.serializer import (
    SignerDetailSerializer,
    SignerInlineSerializer,
)


class MeetingListSerializer(serializers.ModelSerializer):

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    signers_count = serializers.IntegerField(read_only=True)
    signed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "held_at",
            "location",
            "status",
            "created_by",
            "created_by_username",
            "signers_count",
            "signed_count",
            "created_at",
        )


class MeetingDetailSerializer(serializers.ModelSerializer):

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    signers = SignerDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "held_at",
            "location",
            "body",
            "status",
            "content_hash",
            "created_by",
            "created_by_username",
            "signers",
            "created_at",
            "updated_at",
        )


class MeetingCreateSerializer(serializers.ModelSerializer):

    signers = SignerInlineSerializer(
        many=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Meeting
        fields = (
            "id",
            "title",
            "held_at",
            "location",
            "body",
            "signers",
        )
        read_only_fields = ("id",)

    def validate_signers(self, signers):
        user_ids = [s["user"].id for s in signers if s.get("user")]

        if len(user_ids) != len(set(user_ids)):
            raise serializers.ValidationError(
                "یک کاربر نمی‌تواند چند بار امضاکننده باشد."
            )

        return signers

    @transaction.atomic
    def create(self, validated_data):
        signers = validated_data.pop("signers", [])

        meeting = Meeting.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )

        Signer.objects.bulk_create(
            [Signer(meeting=meeting, **s) for s in signers]
        )

        return meeting


class MeetingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = (
            "title",
            "held_at",
            "location",
            "body",
        )

    def validate(self, attrs):
        if not self.instance.is_draft:
            raise serializers.ValidationError(
                "بعد از ارسال برای امضا، متن صورت جلسه قابل ویرایش نیست."
            )
        return attrs
