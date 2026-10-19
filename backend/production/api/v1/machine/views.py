from django.db.models.deletion import ProtectedError

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from access.permissions import ProductionPermission
from production.models.machine import Machine

from .serializers import MachineSerializer


class MachineListView(generics.ListAPIView):

    serializer_class = MachineSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def get_queryset(self):
        queryset = Machine.objects.all()

        # فقط دستگاه‌های فعال: ?is_active=true
        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() in ("1", "true", "yes")
            )

        return queryset


class MachineCreateView(generics.CreateAPIView):

    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class MachineDetailView(generics.RetrieveAPIView):

    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class MachineUpdateView(generics.UpdateAPIView):

    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )


class MachineDeleteView(generics.DestroyAPIView):

    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    permission_classes = (
        IsAuthenticated,
        ProductionPermission,
    )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "این دستگاه دارای ثبت تولید است و قابل حذف نیست. "
                        "به جای حذف، آن را غیرفعال کنید."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
