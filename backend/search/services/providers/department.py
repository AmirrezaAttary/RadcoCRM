from django.db.models import Q

from department.models import Department

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class DepartmentProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Department.objects
            .filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
            )
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.name,
                description=obj.description,
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="department",
                    object_id=obj.id,
                    title=obj.name,
                    subtitle="دپارتمان",
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]