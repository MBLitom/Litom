from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from apps.payments.models import ProjectReviewOrder

from .forms import ClientRegistrationForm


def _safe_next(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return ""


def register(request):
    next_url = _safe_next(request)
    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(next_url or "accounts:dashboard")
    else:
        form = ClientRegistrationForm()
    return render(request, "accounts/register.html", {"form": form, "next": next_url})


@login_required
def dashboard(request):
    orders = ProjectReviewOrder.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/dashboard.html", {"orders": orders})
