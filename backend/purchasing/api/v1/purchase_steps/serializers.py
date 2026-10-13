from rest_framework import serializers

from purchasing.models.purchase_step import PurchaseProcessStep


class PurchaseProcessStepSerializer(serializers.ModelSerializer):

    employees_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseProcessStep
        fields = [
            "id",
            "title",
            "description",
            "order",
            "employees",
            "employees_detail",
        ]

    def get_employees_detail(self, obj):
        return [
            {
                "id": employee.id,
                "employee_id": employee.employee.id,
                "full_name": employee.employee.user.profile.full_name,
                "is_active": employee.is_active,
            }
            for employee in obj.employees.select_related("employee").all()
        ]