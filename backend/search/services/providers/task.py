from django.db.models import Q

from tasks.models.tasks import Task

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class TaskProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            Task.objects
            .select_related(
                "case",
                "case__customer",
                "department",
                "current_step",
            )
            .prefetch_related(
                "assigned_employee",
            )
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(case__title__icontains=query)
                | Q(case__customer__full_name__icontains=query)
                | Q(case__customer__company_name__icontains=query)
                | Q(assigned_employee__full_name__icontains=query)
                | Q(department__name__icontains=query)
                | Q(current_step__name__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            employee_names = [
                employee.full_name
                for employee in obj.assigned_employee.all()
            ]

            score = calculate_match_score(
                query=query,
                title=obj.title,
                description=obj.description,
                extra_fields=[
                    obj.case.title,
                    obj.case.customer.full_name,
                    obj.case.customer.company_name,
                    obj.department.name,
                    obj.current_step.name,
                    *employee_names,
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="task",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle=obj.department.name,
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]