from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "full_name",
            "avatar",
            "email",
            "birth_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]