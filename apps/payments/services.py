import base64
import hashlib
import logging
from urllib.parse import parse_qs, urlencode

from django.conf import settings
from django.core.mail import mail_admins
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.core.notifications import TelegramNotificationService

from .models import PaymentEvent, ProjectReviewOrder

logger = logging.getLogger(__name__)


class PayseraService:
    payment_url = "https://www.paysera.com/pay/"

    def build_payment_url(self, order, request):
        data = {
            "projectid": str(settings.PAYSERA_PROJECT_ID),
            "orderid": order.order_number,
            "amount": str(order.amount_cents),
            "currency": order.currency,
            "accepturl": request.build_absolute_uri(reverse("payments:paysera_accept")),
            "cancelurl": request.build_absolute_uri(reverse("payments:paysera_cancel")),
            "callbackurl": request.build_absolute_uri(reverse("payments:paysera_callback")),
            "version": settings.PAYSERA_VERSION,
            "p_email": order.email,
            "test": "1" if settings.PAYSERA_TEST_MODE else "0",
        }
        encoded_data = self.encode_data(data)
        sign = self.sign(encoded_data)
        order.paysera_request_data = data
        order.save(update_fields=["paysera_request_data", "updated_at"])
        return f"{self.payment_url}?{urlencode({'data': encoded_data, 'sign': sign})}"

    def verify_callback(self, request):
        encoded_data = request.GET.get("data") or request.POST.get("data") or ""
        received_sign = request.GET.get("ss1") or request.POST.get("ss1") or request.GET.get("sign") or request.POST.get("sign") or ""
        raw_payload = {"query": request.GET.dict(), "post": request.POST.dict()}
        if not encoded_data or not received_sign:
            PaymentEvent.objects.create(event_type="callback_missing_signature", raw_data=raw_payload, verified=False)
            return None, {}, False, "missing_signature"
        expected = self.sign(encoded_data)
        data = self.parse_callback_data(encoded_data)
        order = ProjectReviewOrder.objects.filter(order_number=data.get("orderid", "")).first()
        verified = received_sign == expected
        event_type = "callback_verified" if verified else "callback_invalid_signature"
        PaymentEvent.objects.create(order=order, event_type=event_type, raw_data={**raw_payload, "parsed": data}, verified=verified)
        TelegramNotificationService().send_paysera_event(order, event_type, verified=verified)
        if not verified:
            logger.warning("Invalid Paysera callback signature for order %s", data.get("orderid"))
            return order, data, False, "invalid_signature"
        return order, data, True, ""

    def parse_callback_data(self, encoded_data):
        padded = encoded_data.replace("-", "+").replace("_", "/")
        padded += "=" * (-len(padded) % 4)
        decoded = base64.b64decode(padded).decode()
        return {key: values[-1] for key, values in parse_qs(decoded).items()}

    def mark_order_paid(self, order, data):
        if not order:
            return None, "order_not_found"
        with transaction.atomic():
            locked_order = ProjectReviewOrder.objects.select_for_update().get(pk=order.pk)
            if locked_order.status == ProjectReviewOrder.Status.PAID:
                PaymentEvent.objects.create(order=locked_order, event_type="paid_duplicate_callback", raw_data=data, verified=True)
                return locked_order, "already_paid"
            if data.get("orderid") != locked_order.order_number:
                return self._callback_error(locked_order, data, "order_mismatch")
            if str(data.get("amount")) != str(locked_order.amount_cents) or data.get("currency") != locked_order.currency:
                return self._callback_error(locked_order, data, "amount_or_currency_mismatch")
            payment_status = str(data.get("status", "1"))
            if payment_status not in {"1", "paid", "completed", "success"}:
                locked_order.status = ProjectReviewOrder.Status.FAILED
                locked_order.paysera_callback_data = data
                locked_order.save(update_fields=["status", "paysera_callback_data", "updated_at"])
                PaymentEvent.objects.create(order=locked_order, event_type="payment_failed", raw_data=data, verified=True)
                TelegramNotificationService().send_payment_status(locked_order, "failed/cancelled")
                return locked_order, "payment_failed"
            locked_order.status = ProjectReviewOrder.Status.PAID
            locked_order.paysera_callback_data = data
            locked_order.paid_at = timezone.now()
            locked_order.save(update_fields=["status", "paysera_callback_data", "paid_at", "updated_at"])
            PaymentEvent.objects.create(order=locked_order, event_type="payment_marked_paid", raw_data=data, verified=True)
            TelegramNotificationService().send_payment_status(locked_order, "marked as paid")
            self._send_paid_order_email(locked_order)
            return locked_order, "paid"

    def encode_data(self, data):
        query = urlencode(data)
        encoded = base64.b64encode(query.encode()).decode()
        return encoded.replace("+", "-").replace("/", "_").rstrip("=")

    def sign(self, encoded_data):
        return hashlib.md5(f"{encoded_data}{settings.PAYSERA_SIGN_PASSWORD}".encode()).hexdigest()

    def _callback_error(self, order, data, event_type):
        order.status = ProjectReviewOrder.Status.CALLBACK_ERROR
        order.paysera_callback_data = data
        order.save(update_fields=["status", "paysera_callback_data", "updated_at"])
        PaymentEvent.objects.create(order=order, event_type=event_type, raw_data=data, verified=True)
        TelegramNotificationService().send_payment_status(order, "failed/cancelled")
        logger.warning("Paysera callback validation failed for order %s: %s", order.order_number, event_type)
        return order, event_type

    def _send_paid_order_email(self, order):
        try:
            mail_admins(
                subject="MB Litom project review order paid",
                message=(
                    f"Order: {order.order_number}\n"
                    f"Email: {order.email}\n"
                    f"Company: {order.company or '-'}\n"
                    f"Amount: {order.amount_cents / 100:.2f} {order.currency}"
                ),
                fail_silently=True,
            )
        except Exception:
            logger.warning("Admin email notification failed for paid order %s", order.order_number, exc_info=True)
