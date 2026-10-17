from django.contrib import admin
from django.utils.html import format_html

from .models import Meeting, Signer


class SignerInline(admin.TabularInline):

    model = Signer
    extra = 0
    fields = ("user", "full_name", "phone_number", "role_title", "order", "signed_at")
    readonly_fields = ("signed_at",)
    raw_id_fields = ("user",)

    def _locked(self, obj):
        return obj is not None and obj.status != Meeting.Status.DRAFT

    def has_add_permission(self, request, obj=None):
        return not self._locked(obj) and super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return not self._locked(obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return not self._locked(obj) and super().has_delete_permission(request, obj)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "held_at",
        "status",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "held_at",
    )

    search_fields = (
        "title",
        "created_by__username",
    )

    readonly_fields = (
        "status",
        "content_hash",
        "created_by",
        "created_at",
        "updated_at",
    )

    inlines = (SignerInline,)

    actions = ("send_for_signature", "cancel_meetings")

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj is not None and obj.status != Meeting.Status.DRAFT:
            fields += ("title", "held_at", "location", "body")
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="ارسال برای امضا")
    def send_for_signature(self, request, queryset):
        sent = 0
        for meeting in queryset.filter(status=Meeting.Status.DRAFT):
            if meeting.signers.exists():
                meeting.send_for_signature()
                sent += 1
        self.message_user(request, f"{sent} صورت جلسه برای امضا ارسال شد.")

    @admin.action(description="لغو صورت جلسه")
    def cancel_meetings(self, request, queryset):
        qs = queryset.filter(
            status__in=(Meeting.Status.DRAFT, Meeting.Status.PENDING)
        )
        count = 0
        for meeting in qs:
            meeting.cancel()
            count += 1
        self.message_user(request, f"{count} صورت جلسه لغو شد.")


@admin.register(Signer)
class SignerAdmin(admin.ModelAdmin):

    list_display = (
        "meeting",
        "display_name",
        "is_external",
        "role_title",
        "order",
        "is_signed",
        "signed_at",
    )

    list_filter = (
        "meeting__status",
        "signed_at",
    )

    search_fields = (
        "meeting__title",
        "user__username",
        "full_name",
        "phone_number",
        "role_title",
    )

    raw_id_fields = ("meeting", "user")

    readonly_fields = (
        "token",
        "signature_preview",
        "signed_at",
        "signed_ip",
        "signed_hash",
        "created_at",
    )

    exclude = ("signature_image",)

    @admin.display(description="امضا کننده")
    def display_name(self, obj):
        return obj.display_name

    @admin.display(boolean=True, description="بیرونی")
    def is_external(self, obj):
        return obj.is_external

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
