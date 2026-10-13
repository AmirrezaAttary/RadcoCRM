from rest_framework import serializers

from tasks.models import Case, Resource


class ResourceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource

        fields = (
            "id",
            "title",
        )


class ResourceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource

        fields = (
            "title",
        )


class ResourceUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource

        fields = (
            "title",
        )


class ResourceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource

        fields = (
            "id",
            "title",
        )


class CaseListSerializer(serializers.ModelSerializer):

    resources = ResourceListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Case

        fields = (
            "id",
            "customer",
            "created_by",
            "title",
            "resources",
            "active",
            "created_at",
            "updated_at",
        )


class CaseCreateSerializer(serializers.ModelSerializer):

    resources = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Case

        fields = (
            "customer",
            "created_by",
            "title",
            "description",
            "resources",
        )


class CaseUpdateSerializer(serializers.ModelSerializer):

    resources = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Case

        fields = (
            "customer",
            "title",
            "description",
            "resources",
        )


class CaseDetailSerializer(serializers.ModelSerializer):

    resources = ResourceListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Case

        fields = (
            "id",
            "customer",
            "title",
            "description",
            "resources",
            "active",
            "created_at",
            "updated_at",
        )
        
class CaseActivateSerializer(serializers.Serializer):
    pass


class CaseDeactivateSerializer(serializers.Serializer):
    pass