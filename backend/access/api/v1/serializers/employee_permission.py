from rest_framework import serializers

from access.models import EmployeePermission


class EmployeePermissionListSerializer(serializers.ModelSerializer):

    code = serializers.CharField(
        source="permission.code",
        read_only=True,
    )
    resource = serializers.CharField(
        source="permission.resource",
        read_only=True,
    )
    action = serializers.CharField(
        source="permission.action",
        read_only=True,
    )
    name = serializers.CharField(
        source="permission.name",
        read_only=True,
    )
    description = serializers.CharField(
        source="permission.description",
        read_only=True,
    )

    class Meta:
        model = EmployeePermission
        fields = [
            "code",
            "resource",
            "action",
            "name",
            "description",
            "is_active",
        ]

class EmployeePermissionCreateSerializer(serializers.Serializer):

    permission = serializers.CharField()

    def validate_permission(self, value):
        from access.models import Permission

        try:
            permission = Permission.objects.get(
                code=value,
                is_active=True,
            )
        except Permission.DoesNotExist:
            raise serializers.ValidationError(
                "Permission مورد نظر وجود ندارد."
            )

        return permission