from rest_framework import serializers


class CalendarPersonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()


class CalendarPeopleSerializer(serializers.Serializer):
    assigned_employee = CalendarPersonSerializer(
        many=True,
        required=False,
    )
    assigned_to = CalendarPersonSerializer(
        many=True,
        required=False,
    )
    created_by = CalendarPersonSerializer(
        required=False,
        allow_null=True,
    )


class CalendarEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.DateTimeField(allow_null=True)
    end = serializers.DateTimeField(allow_null=True)
    type = serializers.CharField()

    people = CalendarPeopleSerializer(
        required=False,
    )


class CalendarResponseSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    events = CalendarEventSerializer(many=True)