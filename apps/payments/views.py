import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.core.notifications import TelegramNotificationService

from .forms import ProjectReviewOrderForm
from .models import ProjectReviewOrder
from .services import PayseraService

logger = logging.getLogger(__name__)


def project_review_landing(request):
    return render(request, "payments/project_review.html")


@login_required
@require_http_methods(["GET", "POST"])
def project_review_checkout(request):
    if request.method == "POST":
        form = ProjectReviewOrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.amount_cents = 50000
            order.currency = "EUR"
            order.status = ProjectReviewOrder.Status.PENDING_PAYMENT
            order.save()
            TelegramNotificationService().send_project_review_order(order, request)
            messages.success(request, "Your project review order has been created. Complete the payment through Paysera to confirm the review.")
            if settings.PAYSERA_ENABLED and settings.PAYSERA_PROJECT_ID and settings.PAYSERA_SIGN_PASSWORD:
                return redirect(PayseraService().build_payment_url(order, request))
            messages.warning(request, "Paysera checkout is not enabled yet. Your order is saved as pending payment.")
            return redirect("accounts:dashboard")
    else:
        form = ProjectReviewOrderForm(user=request.user)
    return render(request, "payments/checkout.html", {"form": form})


def paysera_accept(request):
    messages.info(request, "Thank you. If the payment was completed, it may take a moment to update after Paysera confirmation.")
    return redirect("accounts:dashboard")


def paysera_cancel(request):
    messages.warning(request, "Payment was cancelled. Your order is still saved and can be restarted.")
    return redirect("accounts:dashboard")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def paysera_callback(request):
    service = PayseraService()
    try:
        order, data, verified, reason = service.verify_callback(request)
        if not verified:
            return HttpResponse("OK", content_type="text/plain")
        service.mark_order_paid(order, data)
    except Exception:
        logger.exception("Paysera callback processing failed")
    return HttpResponse("OK", content_type="text/plain")
