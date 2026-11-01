from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.models import User

AVATAR_MAX_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_ALLOWED_FORMATS = ("JPEG", "PNG", "WEBP")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "phone_number",
            "type",
            "is_active",
            "avatar",
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


class UserSetPasswordSerializer(serializers.Serializer):
    """
    Admin-only: set a new password for a user.
    """

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    def validate_new_password(self, value):
        validate_password(value, user=self.context.get("target_user"))
        return value

    def save(self, **kwargs):
        user = self.context["target_user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, file):
        if file.size > AVATAR_MAX_SIZE:
            raise serializers.ValidationError(
                "حجم عکس نباید بیشتر از ۵ مگابایت باشد."
            )

        image = getattr(file, "image", None)
        if image is None or image.format not in AVATAR_ALLOWED_FORMATS:
            raise serializers.ValidationError(
                "فقط فرمت‌های JPEG، PNG و WEBP مجاز است."
            )

        return file

    def update(self, instance, validated_data):
        # remove the previous file from storage so old photos don't pile up
        if instance.avatar:
            instance.avatar.delete(save=False)

        instance.avatar = validated_data["avatar"]
        instance.save(update_fields=["avatar", "updated_at"])
        return instance
