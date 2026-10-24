from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import (
    Document,
    DocumentFile,
    DocumentStep,
)

from .serializers import (
    DocumentSerializer,
    DocumentFileSerializer,
    DocumentStepSerializer,
)


class DocumentListCreateView(
    generics.ListCreateAPIView
):
    search_fields = (
        "title",
        "created_by__username",
        "created_by__employee_profile__full_name",
    )

    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Document.objects
            .select_related("created_by")
            .prefetch_related(
                "files",
                "steps",
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )


class DocumentDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Document.objects
            .select_related("created_by")
            .prefetch_related(
                "files",
                "steps",
            )
        )


class DocumentFileListCreateView(
    generics.ListCreateAPIView
):
    search_fields = (
        "file",
    )

    serializer_class = DocumentFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs["document_id"]

        return (
            DocumentFile.objects
            .filter(
                document_id=document_id,
            )
            .order_by("-created_at")
        )

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "required": [
                    "file",
                ],
            },
        },
        responses=DocumentFileSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        document_id = self.kwargs["document_id"]

        document = get_object_or_404(
            Document,
            pk=document_id,
        )

        serializer.save(
            document=document,
        )


class DocumentFileDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocumentFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentFile.objects.all()

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "required": [
                    "file",
                ],
            },
        },
        responses=DocumentFileSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    },
                },
            },
        },
        responses=DocumentFileSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(
            request,
            *args,
            **kwargs,
        )


class DocumentStepListCreateView(
    generics.ListCreateAPIView
):
    search_fields = (
        "title",
    )

    serializer_class = DocumentStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs["document_id"]

        return (
            DocumentStep.objects
            .filter(
                document_id=document_id,
            )
            .order_by("order")
        )

    def perform_create(self, serializer):
        document_id = self.kwargs["document_id"]

        document = get_object_or_404(
            Document,
            pk=document_id,
        )

        serializer.save(
            document=document,
        )


class DocumentStepDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocumentStepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentStep.objects.all()