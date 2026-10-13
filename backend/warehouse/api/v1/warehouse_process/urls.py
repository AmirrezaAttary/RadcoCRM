from django.urls import path

from warehouse.api.v1.warehouse_process.views import (
    InventoryStockListView,
    InventoryStockRetrieveView,

    StockTransactionListView,
    StockTransactionRetrieveView,

    InitialStockCreateView,
    StockInView,
    StockOutView,
    
    InventoryStockLimitUpdateView,
)


urlpatterns = [

    path(
        "stock/",
        InventoryStockListView.as_view(),
        name="stock-list",
    ),

    path(
        "stock/<int:pk>/",
        InventoryStockRetrieveView.as_view(),
        name="stock-detail",
    ),

    path(
        "transactions/",
        StockTransactionListView.as_view(),
        name="transaction-list",
    ),

    path(
        "transactions/<int:pk>/",
        StockTransactionRetrieveView.as_view(),
        name="transaction-detail",
    ),

    path(
        "stock/initial/",
        InitialStockCreateView.as_view(),
        name="stock-initial",
    ),

    path(
        "stock/in/",
        StockInView.as_view(),
        name="stock-in",
    ),

    path(
        "stock/out/",
        StockOutView.as_view(),
        name="stock-out",
    ),
    
    path(
        "stock/<int:stock_id>/limits/",
        InventoryStockLimitUpdateView.as_view(),
        name="inventory-stock-limit-update",
    ),
]