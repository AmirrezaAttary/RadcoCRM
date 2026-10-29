from django import forms
from django.contrib import admin

from .models import CustomerOrder, CustomerOrderItem, CustomerPortalAccount


class AccountAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        label="رمز عبور",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="هنگام ساخت الزامی است؛ هنگام ویرایش فقط برای تغییر رمز پر شود.",
    )

    class Meta:
        model = CustomerPortalAccount
        fields = ("customer", "username", "is_active")

    def clean_new_password(self):
        value = self.cleaned_data.get("new_password")
        if not self.instance.pk and not value:
            raise forms.ValidationError("برای حساب جدید رمز عبور لازم است.")
        return value

    def save(self, commit=True):
        account = super().save(commit=False)
        if self.cleaned_data.get("new_password"):
            account.set_password(self.cleaned_data["new_password"])
        if commit:
            account.save()
        return account


@admin.register(CustomerPortalAccount)
class CustomerPortalAccountAdmin(admin.ModelAdmin):
    form = AccountAdminForm
    list_display = ("username", "customer", "is_active", "granted_by", "last_login", "created_at")
    list_filter = ("is_active",)
    search_fields = ("username", "customer__full_name", "customer__phone_number")
    readonly_fields = ("granted_by", "last_login")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


class CustomerOrderItemInline(admin.TabularInline):
    model = CustomerOrderItem
    extra = 0


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer__full_name", "account__username")
    inlines = (CustomerOrderItemInline,)
