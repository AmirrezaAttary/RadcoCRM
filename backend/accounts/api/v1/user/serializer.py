from rest_framework import serializers

from accounts.models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "phone_number",
            "type",
            "is_active",
            "created_at",
            "updated_at",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "phone_number",
            "password",
            "type",
        )

        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "phone_number",
            "type",
            "is_active",
        )