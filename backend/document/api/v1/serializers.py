from rest_framework import serializers

from ...models import (
    Document,
    DocumentFile,
    DocumentStep,
)


class DocumentFileSerializer(serializers.ModelSerializer):
    step = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = DocumentFile
        fields = [
            "id",
            "title",
            "file",
            "step",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "step",
            "created_at",
        ]


class DocumentStepSerializer(serializers.ModelSerializer):
    files = DocumentFileSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = DocumentStep
        fields = [
            "id",
            "order",
            "title",
            "files",
        ]
        read_only_fields = [
            "id",
            "files",
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


class DocumentStepFilePutSerializer(serializers.ModelSerializer):

    step = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = DocumentFile
        fields = [
            "id",
            "title",
            "file",
            "step",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "step",
            "created_at",
        ]


class DocumentStepFilePatchSerializer(serializers.ModelSerializer):

    step = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = DocumentFile
        fields = [
            "id",
            "title",
            "file",
            "step",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "step",
            "created_at",
        ]


class DocumentStepFileDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer مستقل برای endpoint حذف فایل.
    """

    class Meta:
        model = DocumentFile
        fields = [
            "id",
            "title",
            "file",
            "step",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "file",
            "step",
            "created_at",
        ]