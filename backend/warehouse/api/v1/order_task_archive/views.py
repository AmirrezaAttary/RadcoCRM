from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from warehouse.models.order_task_archive import OrderTaskArchive
from warehouse.services.warehouse_scope import scope_by_warehouse

from .serializers import (
    OrderTaskArchiveListSerializer,
    OrderTaskArchiveDetailSerializer,
)


class OrderTaskArchiveListView(generics.ListAPIView):

    search_fields = (
        "title",
        "description",
        "warehouse_name",
        "warehouse_code",
        "product_name",
        "note",
    )

    queryset = (
        OrderTaskArchive.objects
        .select_related(
            "order_task",
        )
        .order_by("-archived_at")
    )

    serializer_class = OrderTaskArchiveListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # warehouse_id روی آرشیو snapshot است (نه FK)
        return scope_by_warehouse(
            super().get_queryset(),
            self.request,
            field="warehouse_id",
        )


class OrderTaskArchiveDetailView(generics.RetrieveAPIView):

    queryset = (
        OrderTaskArchive.objects
        .select_related(
            "order_task",
        )
    )

    serializer_class = OrderTaskArchiveDetailSerializer
    permission_classes = [IsAuthenticated]