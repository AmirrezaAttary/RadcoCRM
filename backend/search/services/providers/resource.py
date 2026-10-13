from tasks.models.cases import Resource

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class ResourceProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = Resource.objects.filter(
            title__icontains=query
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.title,
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="resource",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle="منبع",
                    description=None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]