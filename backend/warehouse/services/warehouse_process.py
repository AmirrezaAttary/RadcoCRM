from django.db import transaction

from warehouse.models.warehouse_process import (
    InventoryStock,
    StockTransaction,
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