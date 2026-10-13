from django.db.models import Q

from warehouse.models.warehouse_order_task import OrderTask

from ..engine import SearchEngine
from ..normalizer import SearchNormalizer
from ..scoring import calculate_match_score


class OrderTaskProvider:

    @staticmethod
    def search(query, user=None, limit=5):

        query = SearchNormalizer.normalize(query)

        queryset = (
            OrderTask.objects
            .select_related(
                "task",
                "case",
                "department",
                "current_step",
                "created_by",
                "performed_by__employee",
            )
            .prefetch_related(
                "assigned_employee",
            )
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(note__icontains=query)
                | Q(case__title__icontains=query)
                | Q(department__name__icontains=query)
                | Q(current_step__name__icontains=query)
                | Q(
                    assigned_employee__full_name__icontains=query
                )
                | Q(created_by__username__icontains=query)
                | Q(
                    performed_by__employee__full_name__icontains=query
                )
                | Q(status__icontains=query)
                | Q(file__icontains=query)
            )
            .distinct()
        )

        results = []

        for obj in queryset:

            employee_names = [
                employee.full_name
                for employee in obj.assigned_employee.all()
            ]

            performed_by_name = (
                obj.performed_by.employee.full_name
                if obj.performed_by
                else None
            )

            current_step_name = (
                obj.current_step.name
                if obj.current_step
                else None
            )

            score = calculate_match_score(
                query=query,
                title=obj.title,
                description=obj.description,
                extra_fields=[
                    obj.note or "",
                    obj.case.title if obj.case else "",
                    obj.department.name if obj.department else "",
                    current_step_name or "",
                    *employee_names,
                    obj.created_by.username
                    if obj.created_by
                    else "",
                    performed_by_name or "",
                    obj.status,
                    obj.get_status_display(),
                    obj.file.name if obj.file else "",
                ],
            )

            if score <= 0:
                continue

            results.append(
                SearchEngine.result(
                    result_type="order_task",
                    object_id=obj.id,
                    title=obj.title,
                    subtitle=current_step_name,
                    description=obj.description or None,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:limit]