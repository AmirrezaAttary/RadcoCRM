# backend/search/services/providers/stock_transaction.py

from django.db.models import Q

from warehouse.models.warehouse_process import StockTransaction

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class StockTransactionProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            StockTransaction.objects
            .select_related(
                "product",
                "performed_by__employee",
            )
            .filter(
                Q(product__name__icontains=query)
                | Q(note__icontains=query)
                | Q(transaction_type__icontains=query)
                | Q(stock_out_reason__icontains=query)
                | Q(
                    performed_by__employee__full_name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            product_name = obj.product.name

            performed_by_name = (
                obj.performed_by.employee.full_name
                if obj.performed_by
                else None
            )

            transaction_type_display = (
                obj.get_transaction_type_display()
            )

            stock_out_reason_display = (
                obj.get_stock_out_reason_display()
                if obj.stock_out_reason
                else ""
            )

            score = calculate_match_score(
                query=query,
                title=product_name,
                description=obj.note,
                extra_fields=[
                    transaction_type_display,
                    obj.transaction_type,
                    stock_out_reason_display,
                    obj.stock_out_reason or "",
                    performed_by_name or "",
                    obj.note or "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="stock_transaction",
                    object_id=obj.id,
                    title=product_name,
                    subtitle=transaction_type_display,
                    description=(
                        obj.note
                        or stock_out_reason_display
                        or None
                    ),
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]