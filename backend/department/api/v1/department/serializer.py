from rest_framework import serializers

from department.models import Department


class DepartmentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "order",
            "created_at",
            "updated_at",
        )


class DepartmentChoiceSerializer(serializers.ModelSerializer):

    # انتقال فقط به دپارتمانی ممکن است که مرحله و مدیر فعال داشته باشد
    has_steps = serializers.SerializerMethodField()
    has_manager = serializers.SerializerMethodField()
    can_receive_tasks = serializers.SerializerMethodField()

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "order",
            "has_steps",
            "has_manager",
            "can_receive_tasks",
        )

    def get_has_steps(self, obj):
        return obj.steps_count > 0

    def get_has_manager(self, obj):
        return obj.active_managers_count > 0

    def get_can_receive_tasks(self, obj):
        return obj.steps_count > 0 and obj.active_managers_count > 0


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
            "created_at",
            "updated_at",
        )