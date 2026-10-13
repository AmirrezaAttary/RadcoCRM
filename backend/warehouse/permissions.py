from access.registry import register_permissions


register_permissions(
    resource="inventory_stocks",
    permissions={
        "list": "مشاهده لیست موجودی انبار",
        "retrieve": "مشاهده جزئیات موجودی انبار",
    },
)

register_permissions(
    resource="warehouse_staff",
    permissions={
        "create": "ایجاد کارمند انبار",
        "update": "ویرایش کارمند انبار",
        "delete": "حذف کارمند انبار",
    },
)