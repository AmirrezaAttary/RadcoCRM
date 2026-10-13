from django.urls import path
from warehouse.api.v1.product.views import (
    ProductCategoryListView, ProductCategoryCreateView,
    ProductCategoryRetrieveView, ProductCategoryUpdateView, ProductCategoryDeleteView,
    ProductListView, ProductCreateView,
    ProductRetrieveView, ProductUpdateView, ProductDeleteView,ProductInitView
)

urlpatterns = [
    # Category
    path("categories/", ProductCategoryListView.as_view(), name="category-list"),
    path("categories/create/", ProductCategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/", ProductCategoryRetrieveView.as_view(), name="category-detail"),
    path("categories/<int:pk>/update/", ProductCategoryUpdateView.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", ProductCategoryDeleteView.as_view(), name="category-delete"),

    # Product
    path("", ProductListView.as_view(), name="product-list"),
    path("create/", ProductCreateView.as_view(), name="product-create"),
    path("<int:pk>/", ProductRetrieveView.as_view(), name="product-detail"),
    path("<int:pk>/update/", ProductUpdateView.as_view(), name="product-update"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"),
    path("create-Init/", ProductInitView.as_view(), name="product-create-Init"),
]
