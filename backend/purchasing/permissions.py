from access.registry import register_permissions


register_permissions(
    resource="purchase_steps",
    permissions={
        "create": "ایجاد مرحله خرید",
        "update": "ویرایش مرحله خرید",
        "delete": "حذف مرحله خرید",
    },
)


register_permissions(
    resource="purchase_process_employees",
    permissions={
        "create": "افزودن کارمند به فرآیند خرید",
        "update": "ویرایش کارمند فرآیند خرید",
        "delete": "حذف کارمند فرآیند خرید",
    },
)