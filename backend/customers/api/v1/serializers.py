from rest_framework import serializers

from customers.models import Customer, CustomerScore

from django.contrib.auth import get_user_model

from accounts.models import Employee

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB



class CustomerExcelImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "حجم فایل نباید بیشتر از ۱۰ مگابایت باشد."
            )

        if not value.name.lower().endswith(".xlsx"):
            raise serializers.ValidationError(
                "فقط فایل Excel با پسوند .xlsx پشتیبانی می‌شود."
            )

        return value


class CustomerListSerializer(serializers.ModelSerializer):

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Customer

        fields = (
            "id",
            "full_name",
            "phone_number",
            "company_name",
            "status",
            "status_display",
            "created_by_username",
            "created_at",
        )


class CustomerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = (
            "full_name",
            "job_title",
            "phone_number",
            "company_name",
            "address",
            "source",
            "description",
            "status",
        )


class CustomerUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = (
            "full_name",
            "job_title",
            "phone_number",
            "company_name",
            "address",
            "source",
            "description",
            "status",
        )


class CustomerDetailSerializer(serializers.ModelSerializer):

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Customer

        fields = (
            "id",
            "full_name",
            "job_title",
            "phone_number",
            "company_name",
            "address",
            "source",
            "description",
            "status",
            "status_display",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        )


class CustomerScoreSerializer(serializers.ModelSerializer):

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
    )

    class Meta:
        model = CustomerScore
        fields = [
            "id",
            "created_by",
            "score",
            "reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]