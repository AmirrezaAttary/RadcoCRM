from django.db.models import Q
from django.db.models import Prefetch

from tasks.models.tasks import TaskStepLog

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class TaskStepLogProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            TaskStepLog.objects
            .select_related(
                "task",
                "step",
            )
            .prefetch_related("employee")
            .filter(
                Q(note__icontains=query)
                | Q(task__title__icontains=query)
                | Q(step__name__icontains=query)
                | Q(employee__full_name__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            employee_names = [
                employee.full_name
                for employee in obj.employee.all()
            ]

            score = calculate_match_score(
                query=query,
                title=obj.task.title,
                description=obj.note,
                extra_fields=[
                    obj.step.name,
                    *employee_names,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="task_step_log",
                    object_id=obj.id,
                    title=obj.task.title,
                    subtitle=obj.step.name,
                    description=obj.note or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]