from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from access.authorization.drf import HasPermission
from access.permissions import PurchasePermission

from purchasing.models.purchase_step import PurchaseProcessStep
from .serializers import PurchaseProcessStepSerializer


class PurchaseProcessStepListView(generics.ListAPIView):

    serializer_class = PurchaseProcessStepSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission
    )

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
            .order_by("order")
        )


class PurchaseProcessStepCreateView(generics.CreateAPIView):

    serializer_class = PurchaseProcessStepSerializer

    required_permission = "purchase_steps.create"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepDetailView(generics.RetrieveAPIView):

    serializer_class = PurchaseProcessStepSerializer

    permission_classes = (
        IsAuthenticated,
        PurchasePermission
    )

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepUpdateView(generics.UpdateAPIView):

    serializer_class = PurchaseProcessStepSerializer

    http_method_names = ["put"]

    required_permission = "purchase_steps.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepPartialUpdateView(generics.UpdateAPIView):

    serializer_class = PurchaseProcessStepSerializer

    http_method_names = ["patch"]

    required_permission = "purchase_steps.update"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return (
            PurchaseProcessStep.objects
            .prefetch_related("employees__employee")
        )


class PurchaseProcessStepDeleteView(generics.DestroyAPIView):

    serializer_class = PurchaseProcessStepSerializer

    required_permission = "purchase_steps.delete"

    permission_classes = (
        IsAuthenticated,
        HasPermission,
    )

    def get_queryset(self):
        return PurchaseProcessStep.objects.all()