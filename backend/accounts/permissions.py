from access.registry import register_permissions


register_permissions(
    resource="employees",
    permissions={
        "create": "ایجاد کارمند",
        "update": "ویرایش کارمند",
        "delete": "حذف کارمند",
    },
)

register_permissions(
    resource="users",
    permissions={
        "create": "ایجاد کاربر",
        "update": "ویرایش کاربر",
        "delete": "حذف کاربر",
    },
)