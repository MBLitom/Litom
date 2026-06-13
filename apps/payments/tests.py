from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .models import PaymentEvent, ProjectReviewOrder
from .services import PayseraService


ORDER_FORM = {
    "full_name": "Ieva Client",
    "email": "ieva@example.com",
    "company": "Client UAB",
    "project_type": "Odoo project rescue",
    "short_description": "We need a paid review of an Odoo integration, current risks, likely scope and next practical milestone direction.",
}


@override_settings(
    PAYSERA_PROJECT_ID="12345",
    PAYSERA_SIGN_PASSWORD="secret",
    PAYSERA_TEST_MODE=True,
    PAYSERA_VERSION="1.9",
    TELEGRAM_NOTIFICATIONS_ENABLED=False,
)
class ProjectReviewPaymentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ieva@example.com",
            email="ieva@example.com",
            password="secure-pass-123",
        )

    def _order(self):
        return ProjectReviewOrder.objects.create(
            user=self.user,
            full_name="Ieva Client",
            email="ieva@example.com",
            company="Client UAB",
            project_type="Odoo",
            short_description="Review the current Odoo project, integration risks, scope and milestone direction.",
            status=ProjectReviewOrder.Status.PENDING_PAYMENT,
        )

    def _signed_callback_params(self, order, **overrides):
        data = {
            "projectid": "12345",
            "orderid": order.order_number,
            "amount": str(order.amount_cents),
            "currency": order.currency,
            "status": "1",
        }
        data.update(overrides)
        service = PayseraService()
        encoded = service.encode_data(data)
        return {"data": encoded, "ss1": service.sign(encoded)}

    def test_anonymous_user_cannot_start_paid_checkout_without_login(self):
        response = self.client.get(reverse("payments:project_review_checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    @override_settings(PAYSERA_ENABLED=False)
    def test_logged_in_user_can_create_project_review_order(self):
        self.client.login(username="ieva@example.com", password="secure-pass-123")
        response = self.client.post(reverse("payments:project_review_checkout"), ORDER_FORM)

        self.assertRedirects(response, reverse("accounts:dashboard"))
        order = ProjectReviewOrder.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, ProjectReviewOrder.Status.PENDING_PAYMENT)

    def test_paysera_payment_url_generation_includes_required_fields(self):
        order = self._order()
        request = RequestFactory().get("/", HTTP_HOST="testserver")
        url = PayseraService().build_payment_url(order, request)
        query = parse_qs(urlparse(url).query)
        data = PayseraService().parse_callback_data(query["data"][0])

        for field in ("projectid", "orderid", "amount", "currency", "accepturl", "cancelurl", "callbackurl", "version"):
            self.assertIn(field, data)
        self.assertEqual(data["amount"], "50000")
        self.assertIn("sign", query)

    def test_paysera_accept_url_does_not_mark_order_as_paid(self):
        order = self._order()
        self.client.force_login(self.user)
        response = self.client.get(reverse("payments:paysera_accept"))

        order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.status, ProjectReviewOrder.Status.PENDING_PAYMENT)

    def test_paysera_callback_with_invalid_signature_does_not_mark_paid(self):
        order = self._order()
        params = self._signed_callback_params(order)
        params["ss1"] = "bad-signature"
        response = self.client.get(reverse("payments:paysera_callback"), params)

        order.refresh_from_db()
        self.assertEqual(response.content, b"OK")
        self.assertEqual(order.status, ProjectReviewOrder.Status.PENDING_PAYMENT)
        self.assertTrue(PaymentEvent.objects.filter(event_type="callback_invalid_signature", verified=False).exists())

    def test_paysera_callback_with_valid_data_marks_order_paid(self):
        order = self._order()
        response = self.client.get(reverse("payments:paysera_callback"), self._signed_callback_params(order))

        order.refresh_from_db()
        self.assertEqual(response.content, b"OK")
        self.assertEqual(order.status, ProjectReviewOrder.Status.PAID)
        self.assertIsNotNone(order.paid_at)

    def test_duplicate_paysera_callback_is_idempotent(self):
        order = self._order()
        params = self._signed_callback_params(order)
        self.client.get(reverse("payments:paysera_callback"), params)
        first_paid_at = ProjectReviewOrder.objects.get(pk=order.pk).paid_at
        self.client.get(reverse("payments:paysera_callback"), params)

        order.refresh_from_db()
        self.assertEqual(order.status, ProjectReviewOrder.Status.PAID)
        self.assertEqual(order.paid_at, first_paid_at)
        self.assertEqual(PaymentEvent.objects.filter(event_type="payment_marked_paid").count(), 1)
        self.assertEqual(PaymentEvent.objects.filter(event_type="paid_duplicate_callback").count(), 1)

    def test_amount_currency_mismatch_does_not_mark_paid(self):
        order = self._order()
        response = self.client.get(reverse("payments:paysera_callback"), self._signed_callback_params(order, amount="999", currency="USD"))

        order.refresh_from_db()
        self.assertEqual(response.content, b"OK")
        self.assertEqual(order.status, ProjectReviewOrder.Status.CALLBACK_ERROR)
        self.assertTrue(PaymentEvent.objects.filter(event_type="amount_or_currency_mismatch").exists())

    def test_dashboard_shows_project_review_order_status(self):
        self._order()
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payment status: pending payment")
