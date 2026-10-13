from django.db.models import Sum

from score.models import Score


DEFAULT_SCORE = 100


def get_employee_score(employee):
    deducted_amount = (
        Score.objects
        .filter(employee=employee)
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    return max(
        0,
        DEFAULT_SCORE - deducted_amount,
    )