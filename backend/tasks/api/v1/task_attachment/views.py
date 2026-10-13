from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema

from access.permissions import TaskPermission

from tasks import services
from tasks.models import Task
from .serializers import (
    TaskAttachmentSerializer,
    TaskAttachmentUploadSerializer,
)


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "binary",
                    },
                },
            },
            "required": ["files"],
        },
    },
    responses=TaskAttachmentSerializer(many=True),
)
class TaskAttachmentCreateApi(generics.GenericAPIView):

    queryset = Task.objects.all()
    serializer_class = TaskAttachmentUploadSerializer
    permission_classes = (IsAuthenticated, TaskPermission)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachments = services.add_task_attachments(
            task=task,
            files=serializer.validated_data["files"],
            uploaded_by=request.user,
        )

        return Response(
            TaskAttachmentSerializer(attachments, many=True).data,
        )