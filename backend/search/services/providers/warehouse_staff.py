# backend/search/services/providers/warehouse_staff.py

from django.db.models import Q

from warehouse.models.warehouse_staff import WarehouseStaff

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class WarehouseStaffProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            WarehouseStaff.objects
            .select_related(
                "employee",
                "employee__user",
            )
            .filter(
                Q(employee__full_name__icontains=query)
                | Q(
                    employee__user__username__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            employee_name = obj.employee.full_name

            username = (
                obj.employee.user.username
                if obj.employee.user
                else ""
            )

            score = calculate_match_score(
                query=query,
                title=employee_name,
                description=None,
                extra_fields=[
                    employee_name,
                    username,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="warehouse_staff",
                    object_id=obj.id,
                    title=employee_name,
                    subtitle="کارمند انبار",
                    description=(
                        "فعال"
                        if obj.is_active
                        else "غیرفعال"
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]