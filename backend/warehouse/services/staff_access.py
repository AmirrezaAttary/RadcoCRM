def ensure_staff_can_access_warehouse(staff, warehouse, exc=ValueError):
    """
    بررسی می‌کند انباردار به انبار مورد نظر دسترسی دارد.
    در غیر این صورت exc (پیش‌فرض ValueError) پرتاب می‌شود.
    """
    if not staff.can_access_warehouse(warehouse):
        raise exc(
            f"انباردار «{staff.employee.full_name}» "
            f"به انبار «{warehouse.name}» دسترسی ندارد."
        )
