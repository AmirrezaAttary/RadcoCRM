from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    پیجینیشن پیش‌فرض همهٔ APIهای لیست.

    ?page=2          → شمارهٔ صفحه
    ?page_size=50    → تعداد آیتم در هر صفحه (حداکثر max_page_size)

    خروجی: {"count", "next", "previous", "results"}
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # اگر کوئری‌ست ترتیب نداشته باشد، صفحه‌بندی ناپایدار می‌شود
        # (ممکن است آیتم‌ها در صفحات تکرار شوند یا جا بمانند).
        if hasattr(queryset, "ordered") and not queryset.ordered:
            queryset = queryset.order_by("pk")
        return super().paginate_queryset(queryset, request, view=view)
