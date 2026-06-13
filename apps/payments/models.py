import uuid

from django.conf import settings
from django.db import models


class ProjectReviewOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"
        CALLBACK_ERROR = "callback_error", "Callback error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="project_review_orders")
    order_number = models.CharField(max_length=40, unique=True, editable=False)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    company = models.CharField(max_length=160, blank=True)
    project_type = models.CharField(max_length=80)
    short_description = models.TextField()
    amount_cents = models.PositiveIntegerField(default=50000)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    paysera_request_data = models.JSONField(blank=True, null=True)
    paysera_callback_data = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PR-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def amount_eur(self):
        return self.amount_cents / 100

    def __str__(self):
        return self.order_number


class PaymentEvent(models.Model):
    PROVIDER_PAYSERA = "paysera"

    order = models.ForeignKey(ProjectReviewOrder, on_delete=models.CASCADE, related_name="payment_events", null=True, blank=True)
    provider = models.CharField(max_length=32, default=PROVIDER_PAYSERA)
    event_type = models.CharField(max_length=80)
    raw_data = models.JSONField(default=dict, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        order = self.order.order_number if self.order else "unknown order"
        return f"{self.provider} {self.event_type} for {order}"
