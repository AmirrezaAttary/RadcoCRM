# backend/search/services/providers/product_category.py

from django.db.models import Q

from warehouse.models.product import ProductCategory

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class ProductCategoryProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = ProductCategory.objects.filter(
            Q(name__icontains=query)
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.name,
                description=None,
                extra_fields=[],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="product_category",
                    object_id=obj.id,
                    title=obj.name,
                    subtitle="دسته‌بندی کالا",
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]