from rest_framework import generics

from purchasing.models.purchase_employee import PurchaseProcessEmployee
from .serializers import PurchaseProcessEmployeeSerializer


class PurchaseProcessEmployeeListView(generics.ListAPIView):
    search_fields = (
        "employee__full_name",
        "employee__user__username",
    )

    serializer_class = PurchaseProcessEmployeeSerializer

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
            .order_by("-joined_at")
        )

class PurchaseProcessEmployeeCreateView(generics.CreateAPIView):
    serializer_class = PurchaseProcessEmployeeSerializer

    def get_queryset(self):
        return PurchaseProcessEmployee.objects.select_related("employee")



class PurchaseProcessEmployeeDetailView(generics.RetrieveAPIView):
    serializer_class = PurchaseProcessEmployeeSerializer

    def get_queryset(self):
        return (
            PurchaseProcessEmployee.objects
            .select_related("employee")
        )


class PurchaseProcessEmployeeUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseProcessEmployeeSerializer
    http_method_names = ["put"]

    def get_queryset(self):
        return PurchaseProcessEmployee.objects.select_related("employee")


class PurchaseProcessEmployeePartialUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseProcessEmployeeSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return PurchaseProcessEmployee.objects.select_related("employee")


class PurchaseProcessEmployeeDeleteView(generics.DestroyAPIView):
    serializer_class = PurchaseProcessEmployeeSerializer

    def get_queryset(self):
        return PurchaseProcessEmployee.objects.select_related("employee")