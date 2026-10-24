from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tasks.models import TaskArchive

from .serializers import (
    TaskArchiveListSerializer,
    TaskArchiveDetailSerializer,
)


class TaskArchiveListView(generics.ListAPIView):

    search_fields = (
        "title",
        "description",
        "customer_full_name",
        "customer_phone_number",
        "customer_company_name",
        "department_name",
        "current_step_name",
        "created_by_full_name",
    )

    queryset = (
        TaskArchive.objects
        .all()
        .order_by("-archived_at")
    )

    serializer_class = TaskArchiveListSerializer
    permission_classes = [IsAuthenticated]


class TaskArchiveDetailView(generics.RetrieveAPIView):

    queryset = TaskArchive.objects.all()

    serializer_class = TaskArchiveDetailSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "id"