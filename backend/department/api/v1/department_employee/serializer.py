from rest_framework import serializers

from department.models import DepartmentEmployee


class DepartmentEmployeeListSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    class Meta:
        model = DepartmentEmployee

        fields = (
            "id",
            "employee",
            "employee_name",
            "department",
            "department_name",
            "created_at",
            "updated_at",
            "is_manager",
        )


class DepartmentEmployeeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentEmployee

        fields = (
            "employee",
            "department",
            "is_manager",
        )


class DepartmentEmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentEmployee

        fields = (
            "department",
            "is_manager",
        )