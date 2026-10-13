from rest_framework import serializers

from warehouse.models.warehouse import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]