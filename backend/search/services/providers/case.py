from django.db.models import Q

from tasks.models.cases import Case

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class CaseProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Case.objects
            .select_related("customer")
            .filter(
                Q(title__icontains=query)
                | Q(customer__full_name__icontains=query)
                | Q(customer__company_name__icontains=query)
                | Q(description__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.title,
                description=obj.description,
                extra_fields=[
                    obj.customer.full_name,
                    obj.customer.company_name,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="case",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle=obj.customer.full_name,
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]