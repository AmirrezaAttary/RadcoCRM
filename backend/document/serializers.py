from rest_framework import serializers

from .models import (
    Document,
    DocumentFile,
    DocumentStep,
)


class DocumentFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentFile

        fields = [
            "id",
            "file",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class DocumentStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentStep

        fields = [
            "id",
            "order",
            "title",
        ]

        read_only_fields = [
            "id",
        ]


class DocumentSerializer(serializers.ModelSerializer):

    files = DocumentFileSerializer(
        many=True,
        read_only=True,
    )

    steps = DocumentStepSerializer(
        many=True,
        read_only=True,
    )

    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Document

        fields = [
            "id",
            "title",
            "created_by",
            "files",
            "steps",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "files",
            "steps",
            "created_at",
            "updated_at",
        ]