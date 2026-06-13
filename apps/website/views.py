import logging

from django.core.cache import cache
from django.core.mail import mail_admins
from django.shortcuts import redirect, render

from apps.core.notifications import TelegramNotificationService
from apps.projects.forms import ProjectRequestForm
from apps.projects.models import ProjectRequest
from apps.projects.spam import detect_project_request_spam

logger = logging.getLogger(__name__)


def homepage(request):
    return render(request, "website/homepage.html")


def services(request):
    return render(request, "website/services.html")


def pricing(request):
    return render(request, "website/pricing.html")


def process(request):
    return render(request, "website/process.html")


def case_studies(request):
    return render(request, "website/case_studies/index.html")


def changeharbor_case_study(request):
    return render(request, "website/case_studies/changeharbor.html")


def odoo_apps_case_study(request):
    return render(request, "website/case_studies/odoo_apps.html")


def contact(request):
    if request.method == "POST":
        form = ProjectRequestForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.ip_address = _client_ip(request)
            inquiry.user_agent = request.META.get("HTTP_USER_AGENT", "")[:1000]
            rate_reason = _rate_limit_reason(inquiry)
            if rate_reason:
                inquiry.is_spam = True
                inquiry.spam_reason = rate_reason
            inquiry.save()
            TelegramNotificationService().send_contact_inquiry(inquiry, request)
            _send_optional_inquiry_email(inquiry)
            return redirect("website:contact_success")
        _store_invalid_spam_attempt(request, form)
    else:
        form = ProjectRequestForm()

    return render(request, "website/contact.html", {"form": form})


def contact_success(request):
    return render(request, "website/contact_success.html")


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _rate_limit_reason(inquiry):
    reasons = []
    for key in (f"contact-ip:{inquiry.ip_address}", f"contact-email:{inquiry.email.lower()}"):
        count = cache.get(key, 0) + 1
        cache.set(key, count, 60 * 60)
        if count > 5:
            reasons.append("rate_limit")
    return ",".join(sorted(set(reasons)))


def _store_invalid_spam_attempt(request, form):
    posted = request.POST
    partial = {
        "full_name": posted.get("full_name", "").strip(),
        "email": posted.get("email", "").strip(),
        "company": posted.get("company", "").strip(),
        "message": posted.get("message", "").strip(),
    }
    reasons = detect_project_request_spam(partial, posted.get("website", ""))
    if not reasons:
        return
    inquiry = ProjectRequest.objects.create(
        full_name=partial["full_name"] or "Unknown",
        email=partial["email"] if "@" in partial["email"] else "spam@example.invalid",
        company=partial["company"],
        project_type=posted.get("project_type") or ProjectRequest.ProjectType.OTHER,
        budget_range=posted.get("budget_range") or ProjectRequest.BudgetRange.NOT_SURE,
        timeline=posted.get("timeline") or ProjectRequest.Timeline.NOT_SURE,
        message=partial["message"] or "(empty spam attempt)",
        is_spam=True,
        spam_reason=",".join(reasons),
        ip_address=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )
    TelegramNotificationService().send_contact_inquiry(inquiry, request)


def _send_optional_inquiry_email(inquiry):
    try:
        mail_admins(
            subject="New MB Litom inquiry",
            message=f"{inquiry.full_name}\n{inquiry.email}\n{inquiry.company}\n\n{inquiry.message}",
            fail_silently=True,
        )
    except Exception:
        logger.warning("Admin email notification failed for inquiry %s", inquiry.pk, exc_info=True)
