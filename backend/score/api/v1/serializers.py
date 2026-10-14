from rest_framework import serializers

from score.models import Score


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = [
            "id", "employee", "task", "department_step", "order_task",
            "action", "amount", "reason", "overdue_period", "created_at",
        ]
        read_only_fields = fields


class EmployeeScoreSerializer(serializers.Serializer):
    employee = serializers.IntegerField()
    score = serializers.IntegerField()
    total_deducted = serializers.IntegerField()
    total_added = serializers.IntegerField()


class ScoreAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = [
            "employee",
            "action",
            "amount",
            "reason",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "مقدار امتیاز باید بیشتر از صفر باشد."
            )
        return value

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "ثبت دلیل تغییر امتیاز الزامی است."
            )
        return value