from django.db.models import Q

from accounts.models import Employee

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class EmployeeProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Employee.objects
            .select_related("user")
            .filter(
                Q(full_name__icontains=query)
                | Q(user__username__icontains=query)
                | Q(user__phone_number__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.full_name,
                extra_fields=[
                    obj.user.username,
                    obj.user.phone_number,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="employee",
                    object_id=obj.id,
                    title=obj.full_name,
                    subtitle="کارمند",
                    description=None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]