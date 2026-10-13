from rest_framework import serializers

from department.models import DepartmentEmployee


class DepartmentEmployeeListSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source="employee.user.profile.full_name",
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
            "active",
            "created_at",
            "updated_at",
        )


class DepartmentEmployeeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentEmployee

        fields = (
            "employee",
            "department",
        )


class DepartmentEmployeeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentEmployee

        fields = (
            "department",
        )


class DepartmentEmployeeDeactivateSerializer(
    serializers.ModelSerializer
):

    employee_name = serializers.CharField(
        source="employee.user.profile.full_name",
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
            "active",
        )

        read_only_fields = (
            "id",
            "employee",
            "employee_name",
            "department",
            "department_name",
            "active",
        )


class DepartmentEmployeeActivateSerializer(
    serializers.ModelSerializer
):

    employee_name = serializers.CharField(
        source="employee.user.profile.full_name",
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
            "active",
        )

        read_only_fields = (
            "id",
            "employee",
            "employee_name",
            "department",
            "department_name",
            "active",
        )