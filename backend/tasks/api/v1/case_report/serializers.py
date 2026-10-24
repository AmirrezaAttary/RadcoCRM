from rest_framework import serializers


class CaseReportQuerySerializer(serializers.Serializer):
    """
    پارامترهای اختیاری گزارش پرونده.
    sections: فقط بخش‌های خواسته‌شده برگردد (برای سبک‌تر شدن پاسخ).
    """

    SECTIONS = (
        "case",
        "customer",
        "summary",
        "tasks",
        "order_tasks",
        "timeline",
    )

    sections = serializers.CharField(
        required=False,
        help_text="لیست جداشده با ویرگول؛ مثلاً summary,tasks",
    )

    def validate_sections(self, value):
        wanted = [s.strip() for s in value.split(",") if s.strip()]
        unknown = [s for s in wanted if s not in self.SECTIONS]
        if unknown:
            raise serializers.ValidationError(
                f"بخش نامعتبر: {', '.join(unknown)}"
            )
        return wanted
