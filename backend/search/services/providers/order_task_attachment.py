from django.db.models import Q

from warehouse.models.warehouse_order_task import OrderTaskAttachment

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class OrderTaskAttachmentProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            OrderTaskAttachment.objects
            .select_related(
                "order_task",
                "order_task__current_step",
                "performed_by__employee",
            )
            .filter(
                Q(note__icontains=query)
                | Q(file__icontains=query)
                | Q(
                    order_task__title__icontains=query
                )
                | Q(
                    order_task__description__icontains=query
                )
                | Q(
                    order_task__current_step__name__icontains=query
                )
                | Q(
                    performed_by__employee__full_name__icontains=query
                )
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            order_task = obj.order_task

            performed_by_name = (
                obj.performed_by.employee.full_name
                if obj.performed_by
                else None
            )

            current_step_name = (
                order_task.current_step.name
                if order_task.current_step
                else ""
            )

            score = calculate_match_score(
                query=query,
                title=order_task.title,
                description=obj.note,
                extra_fields=[
                    obj.note or "",
                    obj.file.name if obj.file else "",
                    order_task.description or "",
                    current_step_name,
                    performed_by_name or "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="order_task_attachment",
                    object_id=obj.id,
                    title=order_task.title,
                    subtitle="پیوست تسک سفارش",
                    description=obj.note or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]