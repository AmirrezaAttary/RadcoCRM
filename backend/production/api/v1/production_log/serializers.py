from decimal import Decimal

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
            "start_time",
            "end_time",
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
            "hours_worked",  # از روی ساعت شروع و پایان محاسبه می‌شود
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

    def _validate_times(self, attrs):
        start = attrs.get(
            "start_time", getattr(self.instance, "start_time", None)
        )
        end = attrs.get(
            "end_time", getattr(self.instance, "end_time", None)
        )

        # ثبت جدید: ساعت شروع و پایان الزامی است
        if self.instance is None:
            missing = {}
            if start is None:
                missing["start_time"] = "ساعت شروع الزامی است."
            if end is None:
                missing["end_time"] = "ساعت پایان الزامی است."
            if missing:
                raise serializers.ValidationError(missing)

        # رکورد قدیمی (بدون ساعت): یا هیچ‌کدام یا هر دو باید داده شوند
        if (start is None) != (end is None):
            raise serializers.ValidationError(
                "ساعت شروع و ساعت پایان باید با هم ثبت شوند."
            )

        if start is not None and start == end:
            raise serializers.ValidationError(
                "ساعت شروع و پایان نمی‌توانند یکسان باشند."
            )

        if start is not None:
            hours = ProductionLog.hours_between(start, end)
            if hours < Decimal("0.01"):
                raise serializers.ValidationError(
                    "مدت کار خیلی کوتاه است."
                )

    def validate(self, attrs):
        self._validate_times(attrs)

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
