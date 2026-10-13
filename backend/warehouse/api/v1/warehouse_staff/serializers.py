from rest_framework import serializers
from warehouse.models.warehouse_staff import WarehouseStaff


class WarehouseStaffSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="employee.user.profile.full_name",
        read_only=True,
    )
    employee_id = serializers.IntegerField(
        source="employee.id",
        read_only=True,
    )

    class Meta:
        model = WarehouseStaff
        fields = [
            "id",
            "employee",
            "employee_id",
            "full_name",
            "is_active",
            "joined_at",
        ]
        read_only_fields = ["joined_at"]
