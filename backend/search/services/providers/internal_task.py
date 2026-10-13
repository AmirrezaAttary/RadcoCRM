from django.db.models import Q

from tasks.models.internal_task import InternalTask

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class InternalTaskProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            InternalTask.objects
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(
                    assigned_to__employee_profile__full_name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            assigned_names = list(
                obj.assigned_to.values_list(
                    "employee_profile__full_name",
                    flat=True,
                )
            )

            score = calculate_match_score(
                query=query,
                title=obj.title,
                description=obj.description,
                extra_fields=assigned_names,
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="internal_task",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle="تسک درون‌سازمانی",
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]