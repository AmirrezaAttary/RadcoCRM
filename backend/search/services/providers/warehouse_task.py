# backend/search/services/providers/warehouse_task.py

from django.db.models import Q

from warehouse.models.warehouse_task import WarehouseTask

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class WarehouseTaskProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            WarehouseTask.objects
            .select_related(
                "purchase_task",
                "purchase_task__process_step",
                "quality_control",
                "product",
                "product__category",
                "assigned_to__employee",
            )
            .filter(
                Q(product__name__icontains=query)
                | Q(
                    purchase_task__product__name__icontains=query
                )
                | Q(
                    purchase_task__process_step__title__icontains=query
                )
                | Q(
                    quality_control__note__icontains=query
                )
                | Q(note__icontains=query)
                | Q(status__icontains=query)
                | Q(
                    assigned_to__employee__full_name__icontains=query
                )
                | Q(file__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            product_name = obj.product.name

            assigned_to_name = (
                obj.assigned_to.employee.full_name
                if obj.assigned_to
                else None
            )

            process_step_title = (
                obj.purchase_task.process_step.title
                if obj.purchase_task
                and obj.purchase_task.process_step
                else None
            )

            score = calculate_match_score(
                query=query,
                title=product_name,
                description=obj.note,
                extra_fields=[
                    obj.purchase_task.product.name
                    if obj.purchase_task
                    and obj.purchase_task.product
                    else "",
                    process_step_title or "",
                    obj.quality_control.note
                    if obj.quality_control
                    else "",
                    obj.status,
                    obj.get_status_display(),
                    assigned_to_name or "",
                    obj.file.name if obj.file else "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="warehouse_task",
                    object_id=obj.id,
                    title=product_name,
                    subtitle=(
                        f"تسک انبار - "
                        f"{obj.get_status_display()}"
                    ),
                    description=obj.note or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]