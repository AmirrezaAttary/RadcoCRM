import hashlib

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from accounts.models import Employee


class Contract(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING = "pending", "در انتظار امضا"
        SIGNED = "signed", "امضا شده"
        CANCELED = "canceled", "لغو شده"

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان قرارداد",
    )

    department = models.ForeignKey(
        "department.Department",
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name="دپارتمان",
    )

    body = models.TextField(
        verbose_name="متن قرارداد",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    # هش متن در لحظه‌ی ارسال برای امضا؛ متن بعد از آن قفل می‌شود
    content_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال برای امضا",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_contracts",
        verbose_name="ایجاد کننده",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-created_at", "-id")
        verbose_name = "قرارداد"
        verbose_name_plural = "قراردادها"

    def __str__(self):
        return self.title

    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT

    def compute_hash(self):
        raw = f"{self.title}|{self.department_id}|{self.body}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_signing_employees(self):
        """
        کارمندان فعالِ دپارتمان در این لحظه
        """
        return Employee.objects.filter(
            is_active=True,
            user__is_active=True,
            department_memberships__department_id=self.department_id,
        ).distinct()

    @transaction.atomic
    def send_for_signature(self):
        """
        از اعضای فعلی دپارتمان یک «جای امضا» می‌سازد و متن را قفل می‌کند.
        عضوهایی که بعداً به دپارتمان اضافه شوند در این قرارداد نمی‌آیند.
        """
        from .signature import ContractSignature

        ContractSignature.objects.bulk_create(
            [
                ContractSignature(contract=self, employee=employee)
                for employee in self.get_signing_employees()
            ],
            ignore_conflicts=True,
        )

        self.content_hash = self.compute_hash()
        self.status = self.Status.PENDING
        self.sent_at = timezone.now()
        self.save(
            update_fields=(
                "content_hash",
                "status",
                "sent_at",
                "updated_at",
            )
        )

    def cancel(self):
        self.status = self.Status.CANCELED
        self.save(update_fields=("status", "updated_at"))

    def refresh_status(self):
        if (
            self.status == self.Status.PENDING
            and not self.signatures.filter(signed_at__isnull=True).exists()
        ):
            self.status = self.Status.SIGNED
            self.save(update_fields=("status", "updated_at"))
