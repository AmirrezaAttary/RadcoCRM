# backend/search/services/providers/product.py

from django.db.models import Q

from warehouse.models.product import Product

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class ProductProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Product.objects
            .select_related("category")
            .filter(
                Q(name__icontains=query)
                | Q(category__name__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            category_name = (
                obj.category.name
                if obj.category
                else None
            )

            unit_type_display = (
                obj.get_unit_type_display()
                if obj.unit_type
                else None
            )

            score = calculate_match_score(
                query=query,
                title=obj.name,
                description=category_name,
                extra_fields=[
                    category_name or "",
                    unit_type_display or "",
                    obj.unit_type or "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="product",
                    object_id=obj.id,
                    title=obj.name,
                    subtitle=category_name,
                    description=(
                        f"نوع واحد: {unit_type_display}"
                        if unit_type_display
                        else None
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]