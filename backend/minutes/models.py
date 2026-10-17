# minutes/models.py
import hashlib, uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Meeting(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING = "pending", "در انتظار امضا"
        SIGNED = "signed", "امضا شده"
        CANCELED = "canceled", "لغو شده"

    title = models.CharField("عنوان", max_length=200)
    held_at = models.DateTimeField("زمان جلسه")
    location = models.CharField("مکان", max_length=200, blank=True)
    body = models.TextField("متن صورت جلسه")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    content_hash = models.CharField(max_length=64, blank=True)  # قفل متن بعد از ارسال برای امضا
    deal = models.ForeignKey("deals.Deal", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="meetings")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="created_meetings")
    created_at = models.DateTimeField(auto_now_add=True)

    def compute_hash(self):
        raw = f"{self.title}|{self.held_at.isoformat()}|{self.body}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def send_for_signature(self):
        self.content_hash = self.compute_hash()
        self.status = self.Status.PENDING
        self.save(update_fields=["content_hash", "status"])

    def refresh_status(self):
        if self.status == self.Status.PENDING and not self.signers.filter(signed_at__isnull=True).exists():
            self.status = self.Status.SIGNED
            self.save(update_fields=["status"])


class Signer(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="signers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    contact = models.ForeignKey("contacts.Contact", null=True, blank=True, on_delete=models.PROTECT)
    role_title = models.CharField("سمت", max_length=100, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # لینک امضا برای افراد خارج از سیستم
    signature_image = models.TextField(blank=True)  # base64 از canvas
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_ip = models.GenericIPAddressField(null=True, blank=True)
    signed_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["order"]

    def sign(self, image_b64, ip):
        self.signature_image = image_b64
        self.signed_at = timezone.now()
        self.signed_ip = ip
        self.signed_hash = self.meeting.content_hash  # اثبات اینکه همین متن امضا شده
        self.save()
        self.meeting.refresh_status()