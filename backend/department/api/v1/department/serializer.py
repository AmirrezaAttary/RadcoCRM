from rest_framework import serializers

from department.models import Department


class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "order",
            "active",
            "created_at",
            "updated_at",
        )


class DepartmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = (
            "name",
            "order",
        )


class DepartmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = (
            "name",
            "order",
        )


class DepartmentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "order",
            "active",
            "created_at",
            "updated_at",
        )