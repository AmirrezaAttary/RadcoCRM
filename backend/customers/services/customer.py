from django.db import transaction

from tasks.exceptions import InvalidTaskActionError


def ensure_customer_active(*, customer):
    if not customer.active:
        raise InvalidTaskActionError(
            "این مشتری غیرفعال است و امکان ایجاد پرونده برای آن وجود ندارد."
        )


@transaction.atomic
def activate_customer(*, customer):
    customer = (
        customer.__class__.objects
        .select_for_update()
        .get(pk=customer.pk)
    )

    if customer.active:
        raise InvalidTaskActionError(
            "این مشتری از قبل فعال است."
        )

    customer.active = True

    customer.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return customer


@transaction.atomic
def deactivate_customer(*, customer):
    customer = (
        customer.__class__.objects
        .select_for_update()
        .get(pk=customer.pk)
    )

    if not customer.active:
        raise InvalidTaskActionError(
            "این مشتری از قبل غیرفعال است."
        )

    customer.active = False

    customer.save(
        update_fields=[
            "active",
            "updated_at",
        ]
    )

    return customer