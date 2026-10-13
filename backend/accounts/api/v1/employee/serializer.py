from rest_framework import serializers

from accounts.models import Employee, User


class EmployeeListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = (
            "id",
            "full_name",
            "username",
            "created_at",
            "updated_at",
        )
    def validate_user(self, user):

        if user.type != User.UserType.EMPLOYEE:
            raise serializers.ValidationError(
                "فقط کاربرانِ کارمند می‌توانند پروفایل کارمندی داشته باشند."
            )

        return user


class EmployeeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "user",
            "full_name",
        )


class EmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "full_name",
        )