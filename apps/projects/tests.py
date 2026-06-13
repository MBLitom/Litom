from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ProjectRequest


VALID_CONTACT = {
    "full_name": "Jonas Petraitis",
    "email": "jonas@example.com",
    "company": "Baltic Ops",
    "project_type": ProjectRequest.ProjectType.WEB_APPLICATION,
    "budget_range": ProjectRequest.BudgetRange.FROM_8000_TO_15000,
    "timeline": ProjectRequest.Timeline.ONE_TO_TWO_MONTHS,
    "message": "We need a business web application that replaces manual spreadsheet work and integrates with our existing operations process.",
}


class ContactFormTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(TELEGRAM_NOTIFICATIONS_ENABLED=False)
    def test_contact_form_accepts_valid_inquiry(self):
        response = self.client.post(reverse("website:contact"), VALID_CONTACT)

        self.assertRedirects(response, reverse("website:contact_success"))
        inquiry = ProjectRequest.objects.get()
        self.assertFalse(inquiry.is_spam)
        self.assertEqual(inquiry.email, "jonas@example.com")

    @override_settings(TELEGRAM_NOTIFICATIONS_ENABLED=False)
    def test_contact_form_rejects_honeypot_submission_and_marks_spam(self):
        payload = {**VALID_CONTACT, "website": "https://spam.example"}
        response = self.client.post(reverse("website:contact"), payload)

        self.assertEqual(response.status_code, 200)
        inquiry = ProjectRequest.objects.get()
        self.assertTrue(inquiry.is_spam)
        self.assertIn("honeypot", inquiry.spam_reason)

    @override_settings(TELEGRAM_NOTIFICATIONS_ENABLED=False)
    def test_contact_form_marks_obvious_test_spam(self):
        payload = {**VALID_CONTACT, "message": "TestTestTestTest"}
        response = self.client.post(reverse("website:contact"), payload)

        self.assertEqual(response.status_code, 200)
        inquiry = ProjectRequest.objects.get()
        self.assertTrue(inquiry.is_spam)
        self.assertIn("test_message", inquiry.spam_reason)

    @override_settings(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_ADMIN_CHAT_ID="123",
    )
    @patch("apps.core.notifications.request.urlopen", side_effect=RuntimeError("network down"))
    def test_telegram_service_failure_does_not_crash_contact_form(self, urlopen):
        response = self.client.post(reverse("website:contact"), VALID_CONTACT)

        self.assertRedirects(response, reverse("website:contact_success"))
        self.assertEqual(ProjectRequest.objects.count(), 1)
        self.assertTrue(urlopen.called)

    def test_anonymous_user_can_access_contact_form(self):
        response = self.client.get(reverse("website:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tell us what you want to build.")
