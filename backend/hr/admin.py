from django.contrib import admin
from django.utils.html import format_html

from .models import Contract, ContractSignature


class ContractSignatureInline(admin.TabularInline):

    model = ContractSignature
    extra = 0
    can_delete = False
    fields = ("employee", "method", "registered_by", "signed_at")
    readonly_fields = ("employee", "method", "registered_by", "signed_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "department",
        "status",
        "created_by",
        "sent_at",
        "created_at",
    )

    list_filter = ("status", "department")

    search_fields = ("title", "created_by__username")

    readonly_fields = (
        "status",
        "content_hash",
        "sent_at",
        "created_by",
        "created_at",
        "updated_at",
    )

    inlines = (ContractSignatureInline,)

    actions = ("send_for_signature", "cancel_contracts")

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj is not None and obj.status != Contract.Status.DRAFT:
            fields += ("title", "department", "body")
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="ارسال برای امضا")
    def send_for_signature(self, request, queryset):
        sent = 0
        for contract in queryset.filter(status=Contract.Status.DRAFT):
            if contract.get_signing_employees().exists():
                contract.send_for_signature()
                sent += 1
        self.message_user(request, f"{sent} قرارداد برای امضا ارسال شد.")

    @admin.action(description="لغو قرارداد")
    def cancel_contracts(self, request, queryset):
        count = 0
        for contract in queryset.filter(
            status__in=(Contract.Status.DRAFT, Contract.Status.PENDING)
        ):
            contract.cancel()
            count += 1
        self.message_user(request, f"{count} قرارداد لغو شد.")


@admin.register(ContractSignature)
class ContractSignatureAdmin(admin.ModelAdmin):

    list_display = (
        "contract",
        "employee",
        "is_signed",
        "method",
        "signed_at",
    )

    list_filter = ("contract__status", "method", "signed_at")

    search_fields = ("contract__title", "employee__full_name")

    raw_id_fields = ("contract", "employee")

    readonly_fields = (
        "signature_preview",
        "method",
        "registered_by",
        "signed_at",
        "signed_ip",
        "signed_hash",
        "created_at",
    )

    exclude = ("signature_image",)

    @admin.display(boolean=True, description="امضا شده")
    def is_signed(self, obj):
        return obj.is_signed

    @admin.display(description="امضا")
    def signature_preview(self, obj):
        if not obj.signature_image:
            return "-"
        return format_html(
            '<img src="{}" style="max-height:80px;background:#fff;border:1px solid #ccc">',
            obj.signature_image,
        )
