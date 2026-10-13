from django.db.models import Q

from customers.models import Customer

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class CustomerProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Customer.objects
            .filter(
                Q(full_name__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(company_name__icontains=query)
                | Q(job_title__icontains=query)
                | Q(description__icontains=query)
                | Q(address__icontains=query)
                | Q(source__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.full_name,
                description=obj.description,
                extra_fields=[
                    obj.phone_number,
                    obj.company_name,
                    obj.job_title,
                    obj.address,
                    obj.source,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="customer",
                    object_id=obj.id,
                    title=obj.full_name,
                    subtitle=obj.company_name or "مشتری",
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]