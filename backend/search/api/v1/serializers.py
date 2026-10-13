from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(
        allow_null=True,
        required=False,
    )
    description = serializers.CharField(
        allow_null=True,
        required=False,
    )
    score = serializers.FloatField()
    url = serializers.CharField()


class SearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    total = serializers.IntegerField()
    results = SearchResultSerializer(many=True)