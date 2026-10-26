from django.core.exceptions import ObjectDoesNotExist

from rest_framework.exceptions import ValidationError


def parse_id_list(raw, name):
    """
    "3" یا "3,5,8" را به [3, 5, 8] تبدیل می‌کند.
    مقدار خالی → None (یعنی فیلتر اعمال نشود).
    """
    if raw is None:
        return None

    raw = str(raw).strip()

    if not raw:
        return None

    ids = []

    for part in raw.split(","):
        part = part.strip()

        if not part:
            continue

        if not part.isdigit():
            raise ValidationError({name: "مقدار نامعتبر است."})

        ids.append(int(part))

    return ids or None


def get_param_ids(params, *names):
    """
    اولین پارامتر پر را از بین names برمی‌گرداند (به‌صورت لیست id).
    مثال: get_param_ids(params, "warehouse_id", "warehouse")
    """
    for name in names:
        ids = parse_id_list(params.get(name), name)

        if ids is not None:
            return ids

    return None


def get_accessible_warehouse_ids(user):
    """
    انبارهایی که کاربر به آن‌ها دسترسی دارد.

    - None  → بدون محدودیت (ادمین / سوپریوزر / کاربری که انباردار نیست)
    - set   → فقط همین انبارها (انباردار فعال با انبارهای مجازش)
              انباردار غیرفعال یا بدون انبار مجاز → set خالی
    """
    if user.is_superuser or user.is_staff:
        return None

    try:
        staff = user.employee_profile.warehouse_staff
    except ObjectDoesNotExist:
        return None

    if not staff.is_active:
        return set()

    return set(staff.warehouses.values_list("pk", flat=True))


def scope_by_warehouse(queryset, request, field="warehouse_id"):
    """
    فیلتر انبار برای لیست‌ها، قبل از صفحه‌بندی و شمارش.

    1) دسترسی کاربر اعمال می‌شود.
    2) اگر ?warehouse_id=3 یا ?warehouse_id=3,5 آمده بود، فقط همان‌ها
       (در محدوده‌ی دسترسی کاربر) برگردانده می‌شود.

    field: مسیر فیلد انبار روی مدل، مثلاً "warehouse_id" یا
           "order_task__warehouse_id"
    """
    allowed = get_accessible_warehouse_ids(request.user)

    requested = get_param_ids(
        request.query_params,
        "warehouse_id",
        "warehouse",
    )

    if allowed is None and requested is None:
        return queryset

    if allowed is None:
        ids = set(requested)
    elif requested is None:
        ids = allowed
    else:
        ids = allowed & set(requested)

    return queryset.filter(**{f"{field}__in": ids})
