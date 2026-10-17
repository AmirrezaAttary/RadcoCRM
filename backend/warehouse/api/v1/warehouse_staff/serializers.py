from rest_framework import serializers
from warehouse.models.warehouse import Warehouse
from warehouse.models.warehouse_staff import WarehouseStaff


class WarehouseStaffSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="employee.full_name", read_only=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True)
    warehouses = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        many=True,
        required=False,
    )
    warehouse_names = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseStaff
        fields = [
            "id", "employee", "employee_id", "full_name",
            "warehouses", "warehouse_names",
            "is_active", "joined_at",
        ]
        read_only_fields = ["joined_at"]

    def get_warehouse_names(self, obj):
        return [w.name for w in obj.warehouses.all()]
