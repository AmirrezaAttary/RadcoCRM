from django.db.models import Q

from tasks.models.internal_task_attachment import InternalTaskAttachment

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class InternalTaskAttachmentProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            InternalTaskAttachment.objects
            .select_related("task")
            .filter(
                Q(original_file_name__icontains=query)
                | Q(note__icontains=query)
                | Q(task__title__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            score = calculate_match_score(
                query=query,
                title=obj.original_file_name,
                description=obj.note,
                extra_fields=[
                    obj.task.title,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="internal_task_attachment",
                    object_id=obj.id,
                    title=obj.original_file_name or "پیوست",
                    subtitle="پیوست تسک درون‌سازمانی",
                    description=obj.task.title,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]