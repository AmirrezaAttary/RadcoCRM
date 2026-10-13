from rest_framework import serializers

from note.models import Note


class NoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id",
            "user",
            "description",
            "created_at",
            "updated_at",
        ]


class NoteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id",
            "user",
            "description",
            "created_at",
            "updated_at",
        ]


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "user",
            "description",
            "created_at",
            "updated_at",
        ]


class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "user",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
        ]