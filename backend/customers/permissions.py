from access.registry import register_permissions


register_permissions(
    resource="customers",
    permissions={
        "list": "مشاهده لیست مشتریان",
        "retrieve": "مشاهده جزئیات مشتری",
        "create": "ایجاد مشتری",
        "update": "ویرایش مشتری",
        "delete": "حذف مشتری",
    },
)