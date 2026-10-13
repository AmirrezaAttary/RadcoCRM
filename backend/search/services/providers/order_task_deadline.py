from django.db.models import Q

from warehouse.models.warehouse_order_task import OrderTaskDeadline

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class OrderTaskDeadlineProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            OrderTaskDeadline.objects
            .select_related(
                "order_task",
                "order_task__current_step",
            )
            .filter(
                Q(order_task__title__icontains=query)
                | Q(
                    order_task__description__icontains=query
                )
                | Q(
                    order_task__current_step__name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            order_task = obj.order_task

            current_step_name = (
                order_task.current_step.name
                if order_task.current_step
                else ""
            )

            score = calculate_match_score(
                query=query,
                title=order_task.title,
                description=order_task.description,
                extra_fields=[
                    current_step_name,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="order_task_deadline",
                    object_id=obj.id,
                    title=order_task.title,
                    subtitle="مهلت تسک سفارش",
                    description=order_task.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]