# search/services/providers/purchase_task.py

from django.db.models import Q

from purchasing.models.purchase_task import PurchaseTask

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class PurchaseTaskProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            PurchaseTask.objects
            .select_related(
                "product",
                "process_step",
            )
            .filter(
                Q(product__name__icontains=query)
                | Q(process_step__title__icontains=query)
                | Q(status__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.product.name,
                description=obj.process_step.title,
                extra_fields=[
                    obj.product.name,
                    obj.process_step.title,
                    obj.status,
                    obj.get_status_display(),
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="purchase_task",
                    object_id=obj.id,
                    title=obj.product.name,
                    subtitle=obj.process_step.title,
                    description=(
                        f"مقدار خرید: {obj.purchase_quantity} | "
                        f"وضعیت: {obj.get_status_display()}"
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]