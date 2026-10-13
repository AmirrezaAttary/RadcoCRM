from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from accounts.models import User


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "نام کاربری یا رمز عبور اشتباه است."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "این حساب کاربری غیرفعال است."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(
                refresh.access_token
            ),

            "refresh": str(
                refresh
            ),

            "user": {
                "id": user.id,
                "username": user.username,
                "phone_number": user.phone_number,
                "type": user.type,
            }
        }


class MeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "phone_number",
            "type",
        )


class RefreshSerializer(TokenRefreshSerializer):
    """
    Wrapper serializer for refresh token.
    """
    pass