from django.db import transaction

from warehouse.models.product import Product
from warehouse.models.warehouse import Warehouse
from warehouse.models.warehouse_staff import WarehouseStaff
from warehouse.models.warehouse_process import StockTransaction
from warehouse.models.warehouse_stock_out import (
    WarehouseStockOut,
    WarehouseStockOutItem,
)

from warehouse.services.warehouse_process import (
    InventoryService,
)
from warehouse.services.staff_access import (
    ensure_staff_can_access_warehouse,
)


class WarehouseStockOutService:

    @staticmethod
    def create_stock_out(
        *,
        warehouse_id,
        performed_by_id,
        items,
        note="",
        file=None,
    ):


        try:

            warehouse = Warehouse.objects.get(
                pk=warehouse_id
            )

        except Warehouse.DoesNotExist:

            raise ValueError(
                "انبار یافت نشد."
            )

        try:

            performed_by = WarehouseStaff.objects.get(
                pk=performed_by_id
            )

        except WarehouseStaff.DoesNotExist:

            raise ValueError(
                "انباردار یافت نشد."
            )

        ensure_staff_can_access_warehouse(
            performed_by,
            warehouse,
        )

        product_ids = [
            item["product_id"]
            for item in items
        ]

        products = Product.objects.in_bulk(
            product_ids
        )

        missing_product_ids = [
            product_id
            for product_id in product_ids
            if product_id not in products
        ]

        if missing_product_ids:

            raise ValueError(
                f"کالاهای زیر یافت نشدند: "
                f"{missing_product_ids}"
            )

        stock_out = (
            WarehouseStockOut.objects.create(
                warehouse=warehouse,
                performed_by=performed_by,
                status=WarehouseStockOut.Status.PENDING,
                note=note,
                file=file,
            )
        )

        for item_data in items:

            product = products[
                item_data["product_id"]
            ]

            reason = item_data.get(
                "reason",
                StockTransaction
                .StockOutReason
                .SALE,
            )

            stock_out_item = (
                WarehouseStockOutItem.objects.create(
                    stock_out=stock_out,
                    product=product,
                    quantity=item_data["quantity"],
                    reason=reason,
                    status=(
                        WarehouseStockOutItem
                        .Status
                        .PENDING
                    ),
                )
            )

            try:

                with transaction.atomic():

                    transaction_obj = (
                        InventoryService.stock_out(
                            warehouse=warehouse,
                            product=product,
                            quantity=item_data[
                                "quantity"
                            ],
                            performed_by_id=performed_by_id,
                            reason=reason,
                            note=note,
                        )
                    )

                    stock_out_item.status = (
                        WarehouseStockOutItem
                        .Status
                        .SUCCESS
                    )

                    stock_out_item.quantity_before = (
                        transaction_obj.quantity_before
                    )

                    stock_out_item.quantity_after = (
                        transaction_obj.quantity_after
                    )

                    stock_out_item.stock_transaction = (
                        transaction_obj
                    )

                    stock_out_item.error_message = None

                    stock_out_item.save(
                        update_fields=[
                            "status",
                            "quantity_before",
                            "quantity_after",
                            "stock_transaction",
                            "error_message",
                            "updated_at",
                        ]
                    )

            except ValueError as exc:

                stock_out_item.status = (
                    WarehouseStockOutItem
                    .Status
                    .FAILED
                )

                stock_out_item.error_message = str(
                    exc
                )

                stock_out_item.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "updated_at",
                    ]
                )

        success_count = (
            stock_out.items
            .filter(
                status=(
                    WarehouseStockOutItem
                    .Status
                    .SUCCESS
                )
            )
            .count()
        )

        failed_count = (
            stock_out.items
            .filter(
                status=(
                    WarehouseStockOutItem
                    .Status
                    .FAILED
                )
            )
            .count()
        )

        if (
            success_count > 0
            and failed_count == 0
        ):

            stock_out.status = (
                WarehouseStockOut
                .Status
                .SUCCESS
            )

        elif (
            success_count > 0
            and failed_count > 0
        ):

            stock_out.status = (
                WarehouseStockOut
                .Status
                .PARTIAL
            )

        else:

            stock_out.status = (
                WarehouseStockOut
                .Status
                .FAILED
            )

        stock_out.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return stock_out