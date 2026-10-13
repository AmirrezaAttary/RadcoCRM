from rest_framework import serializers

from accounts.models import Employee, User


class EmployeeListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    full_name = serializers.CharField(
        source="user.profile.full_name",
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


class EmployeeCreateSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            type=User.UserType.EMPLOYEE,
        ),
    )

    class Meta:
        model = Employee
        fields = (
            "user",
        )


class EmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ()
