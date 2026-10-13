from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.authorization.drf import HasPermission

from purchasing.models.purchase_employee import PurchaseProcessEmployee
from .serializers import PurchaseProcessEmployeeSerializer


class PurchaseProcessEmployeeListView(generics.ListAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
            .order_by("-joined_at")
        )


class PurchaseProcessEmployeeCreateView(generics.CreateAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    required_permission = "purchase_process_employees.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )


class PurchaseProcessEmployeeDetailView(generics.RetrieveAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )


class PurchaseProcessEmployeeUpdateView(generics.UpdateAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    http_method_names = ["put"]

    required_permission = "purchase_process_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )


class PurchaseProcessEmployeePartialUpdateView(generics.UpdateAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    http_method_names = ["patch"]

    required_permission = "purchase_process_employees.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )


class PurchaseProcessEmployeeDeleteView(generics.DestroyAPIView):

    serializer_class = PurchaseProcessEmployeeSerializer

    required_permission = "purchase_process_employees.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )