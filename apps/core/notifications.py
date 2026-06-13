import logging
from urllib import parse, request

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    def __init__(self):
        self.enabled = getattr(settings, "TELEGRAM_NOTIFICATIONS_ENABLED", False)
        self.bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        self.chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "")

    def send_message(self, text):
        if not self.enabled:
            return False
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram notifications enabled without bot token or chat id")
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = parse.urlencode({"chat_id": self.chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
        try:
            with request.urlopen(url, data=payload, timeout=5) as response:
                if response.status >= 400:
                    logger.warning("Telegram notification failed with status %s", response.status)
                    return False
        except Exception:
            logger.exception("Telegram notification failed")
            return False
        return True

    def send_contact_inquiry(self, inquiry, request_obj=None):
        admin_url = self._admin_url("admin:projects_projectrequest_change", inquiry.pk, request_obj)
        label = "Spam/test MB Litom inquiry detected" if inquiry.is_spam else "New MB Litom inquiry"
        text = "\n".join(
            [
                label,
                f"Name: {inquiry.full_name}",
                f"Email: {inquiry.email}",
                f"Company: {inquiry.company or '-'}",
                f"Project type: {inquiry.get_project_type_display()}",
                f"Budget: {inquiry.get_budget_range_display()}",
                f"Timeline: {inquiry.get_timeline_display()}",
                f"Spam reason: {inquiry.spam_reason or '-'}",
                f"Message: {inquiry.message[:900]}",
                f"Admin: {admin_url or '-'}",
            ]
        )
        return self.send_message(text)

    def send_project_review_order(self, order, request_obj=None):
        admin_url = self._admin_url("admin:payments_projectrevieworder_change", order.pk, request_obj)
        text = "\n".join(
            [
                "New paid project review order",
                f"Order: {order.order_number}",
                f"User: {order.user}",
                f"Email: {order.email}",
                f"Amount: {order.amount_cents // 100} {order.currency}",
                f"Status: {order.status}",
                f"Admin: {admin_url or '-'}",
            ]
        )
        return self.send_message(text)

    def send_paysera_event(self, order, event_type, verified=False):
        order_number = order.order_number if order else "unknown"
        text = "\n".join(
            [
                "Paysera payment callback received",
                f"Order: {order_number}",
                f"Event: {event_type}",
                f"Verified: {verified}",
                f"Status: {getattr(order, 'status', '-')}",
            ]
        )
        return self.send_message(text)

    def send_payment_status(self, order, event_type):
        text = "\n".join(
            [
                f"Payment {event_type}",
                f"Order: {order.order_number}",
                f"Email: {order.email}",
                f"Amount: {order.amount_cents // 100} {order.currency}",
                f"Status: {order.status}",
            ]
        )
        return self.send_message(text)

    def _admin_url(self, url_name, pk, request_obj):
        if not request_obj:
            return ""
        path = reverse(url_name, args=[pk])
        return request_obj.build_absolute_uri(path)
