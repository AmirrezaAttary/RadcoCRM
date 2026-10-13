from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tasks.models.internal_task_archive import (
    InternalTaskArchive
)

from .serializers import (
    InternalTaskArchiveListSerializer,
    InternalTaskArchiveDetailSerializer,
)


class InternalTaskArchiveListView(
    generics.ListAPIView
):

    serializer_class = (
        InternalTaskArchiveListSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return (
            InternalTaskArchive.objects
            .all()
            .order_by("-archived_at")
        )


class InternalTaskArchiveRetrieveView(
    generics.RetrieveAPIView
):

    serializer_class = (
        InternalTaskArchiveDetailSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = InternalTaskArchive.objects.all()