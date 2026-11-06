from django.conf import settings
from django.db import models
from django.utils import timezone


class ContractSignature(models.Model):
    """
    امضای یک کارمند پای یک قرارداد.
    امضا دو راه دارد: خود کارمند با حساب کاربری‌اش، یا کارفرما (ادمین)
    که امضای کارمند را می‌گیرد و ثبت می‌کند.
    """

    class Method(models.TextChoices):
        SELF = "self", "توسط خود کارمند"
        EMPLOYER = "employer", "ثبت توسط کارفرما"

    contract = models.ForeignKey(
        "hr.Contract",
        on_delete=models.CASCADE,
        related_name="signatures",
        verbose_name="قرارداد",
    )

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.PROTECT,
        related_name="contract_signatures",
        verbose_name="کارمند",
    )

    # تصویر امضا به صورت data URL (base64)
    signature_image = models.TextField(
        blank=True,
    )

    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان امضا",
    )

    method = models.CharField(
        max_length=10,
        choices=Method.choices,
        blank=True,
        verbose_name="روش امضا",
    )

    # اگر کارفرما ثبت کرده باشد، خودِ او
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="registered_contract_signatures",
        verbose_name="ثبت کننده",
    )

    signed_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    # هش متنی که امضا شده؛ باید با Contract.content_hash برابر باشد
    signed_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("employee__full_name", "id")
        verbose_name = "امضای قرارداد"
        verbose_name_plural = "امضاهای قرارداد"
        constraints = [
            models.UniqueConstraint(
                fields=("contract", "employee"),
                name="unique_signature_per_contract_employee",
            ),
        ]

    def __str__(self):
        return f"{self.contract_id} - {self.employee.full_name}"

    @property
    def is_signed(self):
        return self.signed_at is not None

    def sign(self, signature_image, ip=None, registered_by=None):
        self.signature_image = signature_image
        self.signed_at = timezone.now()
        self.signed_ip = ip
        self.signed_hash = self.contract.content_hash
        self.method = (
            self.Method.EMPLOYER if registered_by else self.Method.SELF
        )
        self.registered_by = registered_by
        self.save(
            update_fields=(
                "signature_image",
                "signed_at",
                "signed_ip",
                "signed_hash",
                "method",
                "registered_by",
            )
        )
        self.contract.refresh_status()
