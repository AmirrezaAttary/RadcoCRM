from access.registry import register_permissions


register_permissions(
    resource="departments",
    permissions={
        "create": "ایجاد دپارتمان",
        "update": "ویرایش دپارتمان",
        "delete": "حذف دپارتمان",
    },
)


register_permissions(
    resource="department_employees",
    permissions={
        "create": "افزودن عضو به دپارتمان",
        "update": "ویرایش عضو دپارتمان",
        "delete": "حذف عضو از دپارتمان",
    },
)


register_permissions(
    resource="department_steps",
    permissions={
        "create": "ایجاد مرحله دپارتمان",
        "update": "ویرایش مرحله دپارتمان",
        "delete": "حذف مرحله دپارتمان",
    },
)