from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from customers.models import Customer, CustomerScore
from .serializers import (
    CustomerListSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerDetailSerializer,
    CustomerScoreSerializer,
)
from . paginations import CustomerPagination

class CustomerListApi(generics.ListAPIView):

    search_fields = (
        "full_name",
        "phone_number",
        "company_name",
        "job_title",
    )

    queryset = Customer.objects.all()

    serializer_class = CustomerListSerializer

    permission_classes = (
        IsAuthenticated,
    )
    # pagination_class = CustomerPagination
    

class CustomerCreateApi(generics.CreateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerCreateSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )


class CustomerDetailApi(generics.RetrieveAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerDetailSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CustomerUpdateApi(generics.UpdateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerUpdateSerializer

    permission_classes = (
        IsAuthenticated,
    )


class CustomerDeleteApi(generics.DestroyAPIView):

    queryset = Customer.objects.all()

    permission_classes = (
        IsAuthenticated,
    )


class CustomerScoreListCreateView(generics.ListCreateAPIView):
    search_fields = (
        "reason",
        "created_by__full_name",
    )

    serializer_class = CustomerScoreSerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]

        return CustomerScore.objects.filter(
            customer_id=customer_id
        ).select_related(
            "customer",
            "created_by",
        )

    def perform_create(self, serializer):
        customer_id = self.kwargs["customer_id"]

        serializer.save(
            customer_id=customer_id
        )


class CustomerScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerScoreSerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]

        return CustomerScore.objects.filter(
            customer_id=customer_id
        ).select_related(
            "customer",
            "created_by",
        )

    def perform_update(self, serializer):
        customer_id = self.kwargs["customer_id"]

        if serializer.validated_data.get("customer"):
            if serializer.validated_data["customer"].id != int(customer_id):
                raise ValidationError({
                    "customer_id": "شناسه مشتری با مشتری موجود در URL مطابقت ندارد."
                })

        serializer.save()