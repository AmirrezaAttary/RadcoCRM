from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from purchasing.models.purchase_task import PurchaseTaskAttachment


from .serializers import (
    PurchaseTaskAttachmentListSerializer,
    PurchaseTaskAttachmentCreateSerializer,
    PurchaseTaskAttachmentDetailSerializer,
    PurchaseTaskAttachmentUpdateSerializer,
    PurchaseTaskAttachmentPartialUpdateSerializer,
    PurchaseTaskAttachmentDeleteSerializer,
)


class PurchaseTaskAttachmentListView(generics.ListAPIView):
    serializer_class = PurchaseTaskAttachmentListSerializer

    def get_queryset(self):
        return (
            PurchaseTaskAttachment.objects
            .select_related(
                "task",
                "process_step",
                "created_by",
                "created_by__employee",
            )
            .order_by("-created_at")
        )


class PurchaseTaskAttachmentCreateView(generics.CreateAPIView):
    queryset = PurchaseTaskAttachment.objects.all()
    serializer_class = PurchaseTaskAttachmentCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            "multipart/form-data": PurchaseTaskAttachmentCreateSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class PurchaseTaskAttachmentDetailView(generics.RetrieveAPIView):
    serializer_class = PurchaseTaskAttachmentDetailSerializer

    def get_queryset(self):
        return (
            PurchaseTaskAttachment.objects
            .select_related(
                "task",
                "process_step",
                "created_by",
                "created_by__employee",
            )
        )


class PurchaseTaskAttachmentUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseTaskAttachmentUpdateSerializer
    http_method_names = ["put"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            PurchaseTaskAttachment.objects
            .select_related(
                "task",
                "process_step",
                "created_by",
                "created_by__employee",
            )
        )


class PurchaseTaskAttachmentPartialUpdateView(generics.UpdateAPIView):
    serializer_class = PurchaseTaskAttachmentPartialUpdateSerializer
    http_method_names = ["patch"]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            PurchaseTaskAttachment.objects
            .select_related(
                "task",
                "process_step",
                "created_by",
                "created_by__employee",
            )
        )


class PurchaseTaskAttachmentDeleteView(generics.DestroyAPIView):
    serializer_class = PurchaseTaskAttachmentDeleteSerializer

    def get_queryset(self):
        return (
            PurchaseTaskAttachment.objects
            .select_related(
                "task",
                "process_step",
                "created_by",
                "created_by__employee",
            )
        )