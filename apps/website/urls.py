from django.urls import path

from .views import (
    case_studies,
    changeharbor_case_study,
    contact,
    contact_success,
    homepage,
    odoo_apps_case_study,
    pricing,
    process,
    services,
)

app_name = "website"

urlpatterns = [
    path("", homepage, name="homepage"),
    path("services/", services, name="services"),
    path("pricing/", pricing, name="pricing"),
    path("process/", process, name="process"),
    path("case-studies/", case_studies, name="case_studies"),
    path("case-studies/changeharbor/", changeharbor_case_study, name="changeharbor_case_study"),
    path("case-studies/odoo-apps/", odoo_apps_case_study, name="odoo_apps_case_study"),
    path("contact/", contact, name="contact"),
    path("contact/success/", contact_success, name="contact_success"),
]
