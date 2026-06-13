from django.urls import path

from .views import paysera_accept, paysera_callback, paysera_cancel, project_review_checkout, project_review_landing

app_name = "payments"

urlpatterns = [
    path("project-review/", project_review_landing, name="project_review_landing"),
    path("project-review/checkout/", project_review_checkout, name="project_review_checkout"),
    path("payments/paysera/accept/", paysera_accept, name="paysera_accept"),
    path("payments/paysera/cancel/", paysera_cancel, name="paysera_cancel"),
    path("payments/paysera/callback/", paysera_callback, name="paysera_callback"),
]
