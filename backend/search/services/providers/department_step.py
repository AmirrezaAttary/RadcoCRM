from django.db.models import Q

from department.models import DepartmentStep

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class DepartmentStepProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            DepartmentStep.objects
            .select_related("department")
            .filter(
                Q(name__icontains=query)
                | Q(department__name__icontains=query)
                | Q(description__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.name,
                description=obj.description,
                extra_fields=[
                    obj.department.name,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="department_step",
                    object_id=obj.id,
                    title=obj.name,
                    subtitle=obj.department.name,
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]