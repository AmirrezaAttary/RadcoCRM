from rest_framework import serializers

from department.models.department_step import DepartmentStep


class DepartmentStepListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentStep

        fields = (
            "id",
            "department",
            "name",
            "order",
            "active",
            "created_at",
            "updated_at",
        )


class DepartmentStepCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentStep

        fields = (
            "department",
            "name",
            "description",
            "order",
        )


class DepartmentStepUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentStep

        fields = (
            "name",
            "description",
            "order",
        )


class DepartmentStepDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DepartmentStep

        fields = (
            "id",
            "department",
            "name",
            "description",
            "order",
            "active",
            "created_at",
            "updated_at",
        )