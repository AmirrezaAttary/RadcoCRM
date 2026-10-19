from rest_framework import serializers

from accounts.models.employee import Employee
from production.models.machine import Machine
from production.models.production_log import ProductionLog


class ProductionLogSerializer(serializers.ModelSerializer):

    # =========================================================
    # Employee (Operator)
    # =========================================================

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.select_related("user"),
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    # =========================================================
    # Machine
    # =========================================================

    machine = serializers.PrimaryKeyRelatedField(
        queryset=Machine.objects.all(),
    )

    machine_name = serializers.CharField(
        source="machine.name",
        read_only=True,
    )

    machine_code = serializers.CharField(
        source="machine.code",
        read_only=True,
    )

    # =========================================================
    # Calculated
    # =========================================================

    expected_production = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True,
    )

    expected_waste = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True,
    )

    efficiency = serializers.FloatField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ProductionLog

        fields = [
            "id",
            "date",

            # Operator
            "employee",
            "employee_name",

            # Machine
            "machine",
            "machine_name",
            "machine_code",

            # Data
            "hours_worked",
            "produced_qty",
            "waste_qty",
            "note",

            # Standards (snapshot) & calculated
            "std_production_per_hour",
            "std_waste_per_hour",
            "expected_production",
            "expected_waste",
            "efficiency",

            # Dates
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "std_production_per_hour",
            "std_waste_per_hour",
            "created_at",
            "updated_at",
        ]

    def validate_employee(self, employee):
        if not employee.is_active:
            raise serializers.ValidationError(
                "این کارمند غیرفعال است."
            )
        return employee

    def validate_machine(self, machine):
        # دستگاه غیرفعال فقط اگر همان دستگاه قبلیِ رکورد باشد مجاز است
        if not machine.is_active and not (
            self.instance and self.instance.machine_id == machine.pk
        ):
            raise serializers.ValidationError(
                "این دستگاه غیرفعال است."
            )
        return machine

    def validate(self, attrs):
        date = attrs.get("date", getattr(self.instance, "date", None))
        employee = attrs.get(
            "employee", getattr(self.instance, "employee", None)
        )
        machine = attrs.get(
            "machine", getattr(self.instance, "machine", None)
        )

        queryset = ProductionLog.objects.filter(
            date=date,
            employee=employee,
            machine=machine,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "برای این کارمند در این تاریخ روی این دستگاه "
                "قبلاً ثبت انجام شده است."
            )

        return attrs
