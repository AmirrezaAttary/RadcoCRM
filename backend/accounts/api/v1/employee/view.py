from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from accounts.models import Employee

from .serializer import (
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
)


class EmployeeListApi(generics.ListAPIView):

    search_fields = (
        "full_name",
        "user__username",
        "user__phone_number",
    )

    queryset = Employee.objects.select_related("user")
    serializer_class = EmployeeListSerializer
    permission_classes = (IsAuthenticated,)


class EmployeeCreateApi(generics.CreateAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateSerializer
    permission_classes = (IsAuthenticated,)


class EmployeeDetailApi(generics.RetrieveAPIView):

    queryset = Employee.objects.select_related("user")
    serializer_class = EmployeeListSerializer
    permission_classes = (IsAuthenticated,)


class EmployeeUpdateApi(generics.UpdateAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeUpdateSerializer
    permission_classes = (IsAuthenticated,)


class EmployeeDeleteApi(generics.DestroyAPIView):

    queryset = Employee.objects.all()
    permission_classes = (IsAuthenticated,)