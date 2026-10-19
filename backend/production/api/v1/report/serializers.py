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
