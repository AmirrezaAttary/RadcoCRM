# search/services/providers/purchase_process_step.py

from django.db.models import Q

from purchasing.models.purchase_step import PurchaseProcessStep

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class PurchaseProcessStepProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            PurchaseProcessStep.objects
            .prefetch_related(
                "employees__employee",
            )
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(
                    employees__employee__full_name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            employee_names = [
                item.employee.full_name
                for item in obj.employees.all()
                if item.employee
            ]

            score = calculate_match_score(
                query=query,
                title=obj.title,
                description=obj.description,
                extra_fields=employee_names,
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="purchase_process_step",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle=f"مرحله {obj.order}",
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]