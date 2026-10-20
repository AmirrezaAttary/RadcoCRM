from rest_framework import serializers


class MonthlyReportQuerySerializer(serializers.Serializer):

    # سال و ماه شمسی؛ مثلاً year=1405 & month=7
    year = serializers.IntegerField(
        min_value=1300,
        max_value=1600,
    )

    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )

    employee_id = serializers.IntegerField(
        required=False,
    )


# ---------------------------------------------------------------------
# گزارش دستگاه‌محور
# ---------------------------------------------------------------------

from datetime import timedelta  # noqa: E402

from production.models.machine import Machine  # noqa: E402
from production.services.machine_report import (  # noqa: E402
    GROUP_BY_CHOICES,
    jalali_year_range,
)
from production.services.report import jalali_month_range  # noqa: E402


class MachineSummaryQuerySerializer(serializers.Serializer):

    # روز / هفته (از شنبه) / ماه شمسی / سال شمسی
    group_by = serializers.ChoiceField(
        choices=GROUP_BY_CHOICES,
        default="day",
    )

    # اگر ندهید، همه‌ی دستگاه‌هایی که در بازه تولید داشته‌اند می‌آیند
    machine_id = serializers.PrimaryKeyRelatedField(
        queryset=Machine.objects.all(),
        required=False,
    )

    # بازه‌ی میلادی (هر دو سر شامل)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    # یا سال/ماه شمسی؛ فقط سال یعنی کل سال
    year = serializers.IntegerField(
        required=False, min_value=1300, max_value=1600,
    )
    month = serializers.IntegerField(
        required=False, min_value=1, max_value=12,
    )

    def validate(self, attrs):
        has_dates = "date_from" in attrs or "date_to" in attrs
        has_jalali = "year" in attrs or "month" in attrs

        if has_dates and has_jalali:
            raise serializers.ValidationError(
                "یا date_from و date_to را بدهید، یا year (و month)؛ هر دو با هم نه."
            )

        if has_dates:
            if "date_from" not in attrs or "date_to" not in attrs:
                raise serializers.ValidationError(
                    "date_from و date_to باید با هم داده شوند."
                )
            if attrs["date_from"] > attrs["date_to"]:
                raise serializers.ValidationError(
                    "date_from نباید بعد از date_to باشد."
                )

        elif has_jalali:
            if "year" not in attrs:
                raise serializers.ValidationError(
                    "برای انتخاب ماه، سال هم لازم است."
                )
            if "month" in attrs:
                start, end = jalali_month_range(attrs["year"], attrs["month"])
            else:
                start, end = jalali_year_range(attrs["year"])
            attrs["date_from"] = start
            attrs["date_to"] = end - timedelta(days=1)

        else:
            raise serializers.ValidationError(
                "بازه را مشخص کنید: date_from و date_to، یا year (و month)."
            )

        days = (attrs["date_to"] - attrs["date_from"]).days + 1

        if days > 3660:
            raise serializers.ValidationError("بازه نباید بیشتر از ۱۰ سال باشد.")

        if attrs["group_by"] == "day" and days > 400:
            raise serializers.ValidationError(
                "برای گروه‌بندی روزانه بازه نباید بیشتر از ۴۰۰ روز باشد."
            )

        return attrs


class MachineMonthlyQuerySerializer(serializers.Serializer):

    year = serializers.IntegerField(min_value=1300, max_value=1600)

    month = serializers.IntegerField(min_value=1, max_value=12)

    machine_id = serializers.PrimaryKeyRelatedField(
        queryset=Machine.objects.all(),
        required=False,
    )
