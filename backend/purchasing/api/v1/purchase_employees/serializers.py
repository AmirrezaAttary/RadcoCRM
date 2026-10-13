from rest_framework import serializers

from purchasing.models.purchase_employee import PurchaseProcessEmployee


class PurchaseProcessEmployeeSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source="employee.user.profile.full_name",
        read_only=True,
    )

    class Meta:
        model = PurchaseProcessEmployee
        fields = [
            "id",
            "employee",
            "employee_name",
            "is_active",
            "joined_at",
        ]
        read_only_fields = [
            "id",
            "joined_at",
        ]
