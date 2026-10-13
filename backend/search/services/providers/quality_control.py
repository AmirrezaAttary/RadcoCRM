# backend/search/services/providers/quality_control.py

from django.db.models import Q

from quality_control.models.quality_control import QualityControl

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class QualityControlProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            QualityControl.objects
            .select_related(
                "purchase_task__product",
                "purchase_task__process_step",
                "checked_by__user",
            )
            .filter(
                Q(
                    purchase_task__product__name__icontains=query
                )
                | Q(
                    purchase_task__process_step__title__icontains=query
                )
                | Q(
                    purchase_task__status__icontains=query
                )
                | Q(status__icontains=query)
                | Q(note__icontains=query)
                | Q(
                    checked_by__user__username__icontains=query
                )
                | Q(file__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            product_name = obj.purchase_task.product.name

            process_step_title = (
                obj.purchase_task.process_step.title
            )

            checked_by_name = (
                obj.checked_by.user.username
                if obj.checked_by
                else None
            )

            score = calculate_match_score(
                query=query,
                title=product_name,
                description=obj.note,
                extra_fields=[
                    process_step_title,
                    obj.purchase_task.status,
                    obj.purchase_task.get_status_display(),
                    obj.status,
                    obj.get_status_display(),
                    obj.note or "",
                    checked_by_name or "",
                    obj.file.name if obj.file else "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="quality_control",
                    object_id=obj.id,
                    title=product_name,
                    subtitle=(
                        f"کنترل کیفیت - "
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