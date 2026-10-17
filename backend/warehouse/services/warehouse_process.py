from django.db import transaction

from warehouse.models.warehouse_process import (
    InventoryStock,
    StockTransaction,
)
from warehouse.services.staff_access import (
    ensure_staff_can_access_warehouse,
)


class InventoryService:

    @staticmethod
    @transaction.atomic
    def add_initial_stock(
        warehouse,
        product,
        quantity: float,
        minimum_stock: float,
        maximum_stock: float,
        performed_by_id: int,
    ) -> InventoryStock:

        if InventoryStock.objects.filter(
            warehouse=warehouse,
            product=product,
        ).exists():
            raise ValueError(
                f"موجودی اول دوره برای {product.name} "
                f"در انبار {warehouse.name} قبلاً ثبت شده است."
            )

        from warehouse.models import WarehouseStaff

        performed_by = WarehouseStaff.objects.filter(
            pk=performed_by_id
        ).first()

        if not performed_by:
            raise ValueError("کاربر انبار یافت نشد.")

        ensure_staff_can_access_warehouse(performed_by, warehouse)

        stock = InventoryStock.objects.create(
            warehouse=warehouse,
            product=product,
            initial_quantity=quantity,
            current_quantity=quantity,
            minimum_stock=minimum_stock,
            maximum_stock=maximum_stock,
        )

        StockTransaction.objects.create(
            warehouse=warehouse,
            product=product,
            transaction_type=StockTransaction.TransactionType.INITIAL,
            quantity_changed=quantity,
            quantity_before=0,
            quantity_after=quantity,
            note="موجودی اول دوره",
            performed_by=performed_by,
        )

        return stock

    @staticmethod
    @transaction.atomic
    def bulk_add_initial_stock(
        warehouse,
        items: list,
        performed_by,
    ) -> list:
        """
        ثبت دسته‌ای موجودی اول دوره (برای ایمپورت اکسل).

        items: لیستی از dict با کلیدهای
               product, quantity, minimum_stock, maximum_stock
        performed_by: خود شیء WarehouseStaff (نه id)
        """

        ensure_staff_can_access_warehouse(performed_by, warehouse)

        product_ids = [item["product"].pk for item in items]

        if len(set(product_ids)) != len(product_ids):
            raise ValueError("یک کالا بیش از یک‌بار در لیست ثبت موجودی آمده است.")

        already = set(
            InventoryStock.objects
            .filter(warehouse=warehouse)
            .values_list("product_id", flat=True)
        ) & set(product_ids)

        if already:
            names = ", ".join(
                item["product"].name
                for item in items
                if item["product"].pk in already
            )
            raise ValueError(
                f"موجودی اول دوره این کالاها در انبار "
                f"{warehouse.name} قبلاً ثبت شده است: {names}"
            )

        stocks = InventoryStock.objects.bulk_create([
            InventoryStock(
                warehouse=warehouse,
                product=item["product"],
                initial_quantity=item["quantity"],
                current_quantity=item["quantity"],
                minimum_stock=item["minimum_stock"],
                maximum_stock=item["maximum_stock"],
            )
            for item in items
        ])

        StockTransaction.objects.bulk_create([
            StockTransaction(
                warehouse=warehouse,
                product=item["product"],
                transaction_type=StockTransaction.TransactionType.INITIAL,
                quantity_changed=item["quantity"],
                quantity_before=0,
                quantity_after=item["quantity"],
                note="موجودی اول دوره",
                performed_by=performed_by,
            )
            for item in items
        ])

        return stocks

    @staticmethod
    @transaction.atomic
    def stock_in(
        warehouse,
        product,
        quantity: float,
        performed_by_id: int,
        note: str = "",
    ) -> StockTransaction:

        if quantity <= 0:
            raise ValueError(
                "مقدار ورود کالا باید بیشتر از صفر باشد."
            )

        from warehouse.models import WarehouseStaff

        try:
            stock = (
                InventoryStock.objects
                .select_for_update()
                .get(
                    warehouse=warehouse,
                    product=product,
                )
            )
        except InventoryStock.DoesNotExist:
            raise ValueError(
                f"موجودی {product.name} در انبار "
                f"{warehouse.name} هنوز ثبت نشده است."
            )

        performed_by = WarehouseStaff.objects.filter(
            pk=performed_by_id
        ).first()

        if not performed_by:
            raise ValueError("کاربر انبار یافت نشد.")

        ensure_staff_can_access_warehouse(performed_by, warehouse)

        before = stock.current_quantity

        stock.current_quantity += quantity

        stock.save(
            update_fields=["current_quantity", "updated_at"]
        )

        return StockTransaction.objects.create(
            warehouse=warehouse,
            product=product,
            transaction_type=StockTransaction.TransactionType.STOCK_IN,
            quantity_changed=quantity,
            quantity_before=before,
            quantity_after=stock.current_quantity,
            note=note,
            performed_by=performed_by,
        )

    @staticmethod
    @transaction.atomic
    def stock_out(
        warehouse,
        product,
        quantity: float,
        performed_by_id: int,
        reason: str = StockTransaction.StockOutReason.SALE,
        note: str = "",
    ) -> StockTransaction:

        if quantity <= 0:
            raise ValueError(
                "مقدار خروج کالا باید بیشتر از صفر باشد."
            )

        from warehouse.models import WarehouseStaff
        from purchasing.services.purchase_service import PurchaseService

        try:
            stock = (
                InventoryStock.objects
                .select_for_update()
                .get(
                    warehouse=warehouse,
                    product=product,
                )
            )
        except InventoryStock.DoesNotExist:
            raise ValueError(
                f"موجودی {product.name} در انبار "
                f"{warehouse.name} هنوز ثبت نشده است."
            )

        if quantity > stock.current_quantity:
            raise ValueError(
                f"موجودی کافی نیست. "
                f"موجودی جاری در انبار {warehouse.name}: "
                f"{stock.current_quantity}"
            )

        performed_by = WarehouseStaff.objects.filter(
            pk=performed_by_id
        ).first()

        if not performed_by:
            raise ValueError("کاربر انبار یافت نشد.")

        ensure_staff_can_access_warehouse(performed_by, warehouse)

        before = stock.current_quantity

        stock.current_quantity -= quantity

        stock.save(
            update_fields=["current_quantity", "updated_at"]
        )

        transaction_obj = StockTransaction.objects.create(
            warehouse=warehouse,
            product=product,
            transaction_type=StockTransaction.TransactionType.STOCK_OUT,
            quantity_changed=quantity,
            quantity_before=before,
            quantity_after=stock.current_quantity,
            stock_out_reason=reason,
            note=note,
            performed_by=performed_by,
        )

        if stock.current_quantity < stock.minimum_stock:
            PurchaseService.create_purchase_task(
                product=product,
                stock=stock,
            )

        return transaction_obj