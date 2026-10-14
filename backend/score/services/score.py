from django.db.models import Case, IntegerField, Sum, When

from score.models import Score

DEFAULT_SCORE = 100


def get_score_totals(employee):
    totals = Score.objects.filter(employee=employee).aggregate(
        deducted=Sum(
            Case(
                When(action=Score.Action.DEDUCT, then="amount"),
                default=0,
                output_field=IntegerField(),
            )
        ),
        added=Sum(
            Case(
                When(action=Score.Action.ADD, then="amount"),
                default=0,
                output_field=IntegerField(),
            )
        ),
    )
    return totals["deducted"] or 0, totals["added"] or 0


def get_employee_score(employee):
    deducted, added = get_score_totals(employee)
    return max(0, DEFAULT_SCORE - deducted + added)