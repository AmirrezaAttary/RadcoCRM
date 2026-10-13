from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Employee
from score.models import Score

from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .serializers import (
    EmployeeScoreSerializer,
    ScoreSerializer,
    ScoreAdjustmentSerializer
)


class EmployeeScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeScoreSerializer

    def get(self, request, employee_id):
        employee = get_object_or_404(
            Employee,
            id=employee_id,
        )

        total_deducted = (
            Score.objects
            .filter(employee=employee)
            .aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        score = max(
            0,
            100 - total_deducted,
        )

        data = {
            "employee": employee.id,
            "score": score,
            "total_deducted": total_deducted,
        }

        serializer = self.get_serializer(data)

        return Response(serializer.data)


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
    permission_classes = [IsAdminUser]
    serializer_class = ScoreAdjustmentSerializer

    @transaction.atomic
    def post(self, request, employee_id):
        employee = generics.get_object_or_404(
            Employee,
            id=employee_id,
        )

        serializer = self.get_serializer(data={
            **request.data,
            "employee": employee.id,
        })
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