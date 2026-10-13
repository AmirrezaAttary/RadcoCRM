from rest_framework import serializers

from access.models import Permission


class PermissionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = [
            "code",
            "resource",
            "action",
            "name",
            "description",
        ]