from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from access.authorization.drf import HasPermission

from customers.models import Customer, CustomerScore
from customers.services.customer import (
    activate_customer,
    deactivate_customer,
)

from .serializers import (
    CustomerListSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerDetailSerializer,
    CustomerActivateSerializer,
    CustomerDeactivateSerializer,
    CustomerScoreSerializer,
)

class CustomerListApi(generics.ListAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerListSerializer

    required_permission = "customers.list"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]



class CustomerCreateApi(generics.CreateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerCreateSerializer

    required_permission = "customers.create"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )


class CustomerDetailApi(generics.RetrieveAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerDetailSerializer

    required_permission = "customers.retrieve"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]


class CustomerUpdateApi(generics.UpdateAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerUpdateSerializer

    required_permission = "customers.update"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]


class CustomerDeleteApi(generics.DestroyAPIView):

    queryset = Customer.objects.all()

    required_permission = "customers.delete"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]


class CustomerScoreListCreateView(generics.ListCreateAPIView):
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
        
class CustomerActivateApi(generics.GenericAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerActivateSerializer

    required_permission = "customers.activate"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    def post(self, request, pk):

        customer = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        customer = activate_customer(
            customer=customer,
        )

        return Response(
            CustomerDetailSerializer(
                customer,
            ).data
        )


class CustomerDeactivateApi(generics.GenericAPIView):

    queryset = Customer.objects.all()

    serializer_class = CustomerDeactivateSerializer

    required_permission = "customers.deactivate"

    permission_classes = [
        IsAuthenticated,
        HasPermission,
    ]

    def post(self, request, pk):

        customer = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        customer = deactivate_customer(
            customer=customer,
        )

        return Response(
            CustomerDetailSerializer(
                customer,
            ).data
        )