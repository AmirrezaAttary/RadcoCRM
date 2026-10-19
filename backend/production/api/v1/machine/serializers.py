from rest_framework import serializers

from production.models.machine import Machine


class MachineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Machine
        fields = [
            "id",
            "name",
            "code",
            "std_production_per_hour",
            "std_waste_per_hour",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_std_production_per_hour(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "تولید استاندارد نمی‌تواند منفی باشد."
            )
        return value

    def validate_std_waste_per_hour(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "ضایعات استاندارد نمی‌تواند منفی باشد."
            )
        return value
