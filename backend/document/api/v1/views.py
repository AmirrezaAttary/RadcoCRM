from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated

from ...models import (
    Document,
    DocumentFile,
    DocumentStep,
)

from .serializers import (
    DocumentSerializer,
    DocumentFileSerializer,
    DocumentStepSerializer,
    DocumentStepFilePutSerializer,
    DocumentStepFilePatchSerializer,
    DocumentStepFileDeleteSerializer,
)


FILE_UPLOAD_SCHEMA = {
    "multipart/form-data": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
            },
            "file": {
                "type": "string",
                "format": "binary",
            },
        },
        "required": [
            "title",
            "file",
        ],
    },
}


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
                "steps__files",
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
                "steps__files",
            )
        )


class DocumentFileListCreateView(
    generics.ListCreateAPIView
):
    search_fields = (
        "title",
        "file",
    )

    serializer_class = DocumentFileSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        document_id = self.kwargs["document_id"]

        return (
            DocumentFile.objects
            .filter(
                document_id=document_id,
                step__isnull=True,
            )
            .order_by("-created_at")
        )

    @extend_schema(
        request=FILE_UPLOAD_SCHEMA,
        responses=DocumentFileSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        document = get_object_or_404(
            Document,
            pk=self.kwargs["document_id"],
        )

        serializer.save(
            document=document,
        )


class DocumentFileDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocumentFileSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):
        return DocumentFile.objects.all()

    @extend_schema(
        request=FILE_UPLOAD_SCHEMA,
        responses=DocumentFileSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        request=FILE_UPLOAD_SCHEMA,
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
            .prefetch_related("files")
            .order_by("order")
        )

    def perform_create(self, serializer):
        document = get_object_or_404(
            Document,
            pk=self.kwargs["document_id"],
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
        return (
            DocumentStep.objects
            .prefetch_related("files")
        )


class DocumentStepFileListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = DocumentFileSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_step(self):
        return get_object_or_404(
            DocumentStep.objects.select_related(
                "document",
            ),
            pk=self.kwargs["step_id"],
            document_id=self.kwargs["document_id"],
        )

    def get_queryset(self):
        step = self.get_step()

        return (
            DocumentFile.objects
            .filter(
                document=step.document,
                step=step,
            )
            .order_by("-created_at")
        )

    @extend_schema(
        request=FILE_UPLOAD_SCHEMA,
        responses=DocumentFileSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        step = self.get_step()

        serializer.save(
            document=step.document,
            step=step,
        )

class DocumentStepFilePutView(generics.UpdateAPIView):

    serializer_class = DocumentStepFilePutSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    http_method_names = [
        "put",
        "options",
        "head",
    ]

    def get_queryset(self):
        return DocumentFile.objects.filter(
            document_id=self.kwargs["document_id"],
            step_id=self.kwargs["step_id"],
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["file_id"],
        )

    @extend_schema(
        request=DocumentStepFilePutSerializer,
        responses=DocumentStepFilePutSerializer,
    )
    def put(self, request, *args, **kwargs):
        return super().put(
            request,
            *args,
            **kwargs,
        )


class DocumentStepFilePatchView(generics.UpdateAPIView):

    serializer_class = DocumentStepFilePatchSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    http_method_names = [
        "patch",
        "options",
        "head",
    ]

    def get_queryset(self):
        return DocumentFile.objects.filter(
            document_id=self.kwargs["document_id"],
            step_id=self.kwargs["step_id"],
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["file_id"],
        )

    @extend_schema(
        request=DocumentStepFilePatchSerializer,
        responses=DocumentStepFilePatchSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(
            request,
            *args,
            **kwargs,
        )


class DocumentStepFileDeleteView(generics.DestroyAPIView):

    serializer_class = DocumentStepFileDeleteSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "delete",
        "options",
        "head",
    ]

    def get_queryset(self):
        return DocumentFile.objects.filter(
            document_id=self.kwargs["document_id"],
            step_id=self.kwargs["step_id"],
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["file_id"],
        )