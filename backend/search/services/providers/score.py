from django.db.models import Q

from score.models import Score

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class ScoreProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Score.objects
            .select_related(
                "employee",
                "task",
                "department_step",
            )
            .filter(
                Q(reason__icontains=query)
                | Q(employee__full_name__icontains=query)
                | Q(task__title__icontains=query)
                | Q(department_step__name__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            task_title = (
                obj.task.title
                if obj.task
                else None
            )

            step_name = (
                obj.department_step.name
                if obj.department_step
                else None
            )

            score = calculate_match_score(
                query=query,
                title=obj.reason,
                extra_fields=[
                    obj.employee.full_name,
                    task_title,
                    step_name,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="score",
                    object_id=obj.id,
                    title=obj.reason,
                    subtitle=obj.employee.full_name,
                    description=task_title,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]