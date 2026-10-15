from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from accounts.models import Employee
from department.models import DepartmentEmployee
from score.models import Score
from score.services.score import get_employee_score, get_score_totals

from .serializers import (
    EmployeeScoreSerializer,
    ScoreSerializer,
    ScoreAdjustmentSerializer,
)


class IsAdminOrDepartmentManager(BasePermission):
    """
    اجازه دسترسی به ادمین یا مدیر دپارتمان.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        return DepartmentEmployee.objects.filter(
            employee=user,
            is_manager=True,
        ).exists()


class EmployeeScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeScoreSerializer

    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee,
            id=employee_id,
        )

        total_deducted, total_added = get_score_totals(employee)

        data = {
            "employee": employee.id,
            "score": get_employee_score(employee),
            "total_deducted": total_deducted,
            "total_added": total_added,
        }

        return Response(self.get_serializer(data).data)


class EmployeeScoreHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScoreSerializer

    def get_queryset(self):
        employee_id = self.kwargs["employee_id"]

        return (
            Score.objects
            .filter(employee_id=employee_id)
            .select_related(
                "employee",
                "task",
                "department_step",
                "order_task",
            )
        )


class AdminScoreAdjustmentView(generics.GenericAPIView):
    permission_classes = [IsAdminOrDepartmentManager]
    serializer_class = ScoreAdjustmentSerializer

    @transaction.atomic
    def post(self, request, employee_id):
        employee = get_object_or_404(
            Employee,
            id=employee_id,
        )

        serializer = self.get_serializer(
            data={
                **request.data,
                "employee": employee.id,
            }
        )
        serializer.is_valid(raise_exception=True)

        score_log = serializer.save()

        return Response(
            {
                "message": "امتیاز کارمند با موفقیت تغییر کرد.",
                "employee": employee.id,
                "action": score_log.action,
                "amount": score_log.amount,
                "reason": score_log.reason,
                "score_log_id": score_log.id,
            },
            status=status.HTTP_201_CREATED,
        )