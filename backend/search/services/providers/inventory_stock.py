# backend/search/services/providers/inventory_stock.py

from django.db.models import Q

from warehouse.models.warehouse_process import InventoryStock

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class InventoryStockProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            InventoryStock.objects
            .select_related(
                "product",
                "product__category",
            )
            .filter(
                Q(product__name__icontains=query)
                | Q(
                    product__category__name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            product_name = obj.product.name

            category_name = (
                obj.product.category.name
                if obj.product.category
                else None
            )

            unit_label = obj._get_unit_label()

            score = calculate_match_score(
                query=query,
                title=product_name,
                description=category_name,
                extra_fields=[
                    category_name or "",
                    unit_label,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="inventory_stock",
                    object_id=obj.id,
                    title=product_name,
                    subtitle=f"موجودی: {obj.current_quantity} {unit_label}",
                    description=(
                        f"حداقل: {obj.minimum_stock} | "
                        f"حداکثر: {obj.maximum_stock}"
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]