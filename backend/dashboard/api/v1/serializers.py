from rest_framework import serializers

PERIOD_CHOICES = ("weekly", "monthly", "yearly")


class PeriodQuerySerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=PERIOD_CHOICES, default="monthly")


class TopExpertsQuerySerializer(PeriodQuerySerializer):
    limit = serializers.IntegerField(min_value=1, max_value=20, default=5)


class OverviewQuerySerializer(serializers.Serializer):
    sales = serializers.ChoiceField(choices=PERIOD_CHOICES, default="monthly")
    sources = serializers.ChoiceField(choices=PERIOD_CHOICES, default="weekly")
    cancelled = serializers.ChoiceField(choices=PERIOD_CHOICES, default="monthly")
    experts = serializers.ChoiceField(choices=PERIOD_CHOICES, default="monthly")
