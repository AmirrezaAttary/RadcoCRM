from rest_framework import generics

from purchasing.models.purchase_step import PurchaseProcessStep
from .serializers import PurchaseProcessStepSerializer


class PurchaseProcessStepListView(generics.ListAPIView):
    serializer_class = PurchaseProcessStepSerializer

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
            .order_by("order")
        )


class PurchaseProcessStepCreateView(generics.CreateAPIView):
    serializer_class = PurchaseProcessStepSerializer

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepDetailView(generics.RetrieveAPIView):
    serializer_class = PurchaseProcessStepSerializer

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseProcessStepSerializer
    http_method_names = ["put"]

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepPartialUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseProcessStepSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepDeleteView(generics.DestroyAPIView):
    serializer_class = PurchaseProcessStepSerializer

    def get_queryset(self):
        return PurchaseProcessStep.objects.all()