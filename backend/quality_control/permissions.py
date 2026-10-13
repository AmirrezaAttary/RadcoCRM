from access.registry import register_permissions


register_permissions(
    resource="quality_control_employees",
    permissions={
        "create": "ایجاد کارمند کنترل کیفیت",
        "update": "ویرایش کارمند کنترل کیفیت",
        "delete": "حذف کارمند کنترل کیفیت",
    },
)