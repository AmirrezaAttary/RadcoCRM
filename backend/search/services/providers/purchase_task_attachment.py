# search/services/providers/purchase_task_attachment.py

from django.db.models import Q

from purchasing.models.purchase_task import PurchaseTaskAttachment

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class PurchaseTaskAttachmentProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            PurchaseTaskAttachment.objects
            .select_related(
                "task__product",
                "task__process_step",
                "process_step",
                "created_by__employee",
            )
            .filter(
                Q(note__icontains=query)
                | Q(file__icontains=query)
                | Q(task__product__name__icontains=query)
                | Q(task__process_step__title__icontains=query)
                | Q(process_step__title__icontains=query)
                | Q(
                    created_by__employee__full_name__icontains=query
                )
                | Q(type__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            product_name = obj.task.product.name

            process_step_title = (
                obj.process_step.title
                if obj.process_step
                else obj.task.process_step.title
            )

            created_by_name = obj.created_by.employee.full_name

            score = calculate_match_score(
                query=query,
                title=product_name,
                description=obj.note,
                extra_fields=[
                    obj.note or "",
                    obj.file.name if obj.file else "",
                    process_step_title,
                    created_by_name,
                    obj.type,
                    obj.get_type_display(),
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="purchase_task_attachment",
                    object_id=obj.id,
                    title=product_name,
                    subtitle=process_step_title,
                    description=obj.note or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]