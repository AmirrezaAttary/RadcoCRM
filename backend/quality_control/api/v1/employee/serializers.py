from rest_framework import serializers

from accounts.models.user import User
from quality_control.models.employee import QualityControlEmployee


class QualityControlEmployeeSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = QualityControlEmployee
        fields = [
            "id",
            "user",
            "username",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_user(self, user):
        queryset = QualityControlEmployee.objects.filter(
            user=user
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "این کاربر قبلاً به عنوان کارمند کنترل کیفیت ثبت شده است."
            )

        return user
