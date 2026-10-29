import secrets
import string

from django.db.models import Q, Sum

from warehouse.models.product import Product


def generate_password(length=10):
    """رمز تصادفی خوانا (بدون حروف/ارقام مشابه مثل O/0 و l/1)."""
    alphabet = "".join(
        c for c in string.ascii_letters + string.digits if c not in "O0Il1"
    )
    return "".join(secrets.choice(alphabet) for _ in range(length))


def products_with_stock():
    """
    کالاهایی که مجموع موجودی‌شان در انبارهای «فعال» بیشتر از صفر است،
    همراه با فیلد available_quantity.
    """
    return Product.objects.annotate(
        available_quantity=Sum(
            "inventory_stocks__current_quantity",
            filter=Q(inventory_stocks__warehouse__is_active=True),
        )
    ).filter(available_quantity__gt=0)
