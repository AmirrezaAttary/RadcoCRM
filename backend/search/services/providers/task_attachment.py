from django.db.models import Q

from tasks.models.task_attachment import TaskAttachment

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class TaskAttachmentProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            TaskAttachment.objects
            .select_related(
                "task",
                "task_step_log",
            )
            .filter(
                Q(original_file_name__icontains=query)
                | Q(task__title__icontains=query)
                | Q(task_step_log__task__title__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            task_title = None

            if obj.task:
                task_title = obj.task.title

            elif obj.task_step_log:
                task_title = obj.task_step_log.task.title

            score = calculate_match_score(
                query=query,
                title=obj.original_file_name,
                extra_fields=[
                    task_title,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="task_attachment",
                    object_id=obj.id,
                    title=obj.original_file_name or "پیوست",
                    subtitle="پیوست تسک",
                    description=task_title,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]