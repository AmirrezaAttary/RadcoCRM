# backend/search/services/providers/quality_control_employee.py

from django.db.models import Q

from quality_control.models.employee import QualityControlEmployee

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class QualityControlEmployeeProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            QualityControlEmployee.objects
            .select_related("user")
            .filter(
                Q(user__username__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            username = obj.user.username

            score = calculate_match_score(
                query=query,
                title=username,
                description=None,
                extra_fields=[
                    username,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="quality_control_employee",
                    object_id=obj.id,
                    title=username,
                    subtitle="کارمند کنترل کیفیت",
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