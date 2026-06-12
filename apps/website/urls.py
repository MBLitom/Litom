from django.urls import path

from .views import (
    changeharbor_case_study,
    contact,
    homepage,
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
    path("case-studies/changeharbor/", changeharbor_case_study, name="changeharbor_case_study"),
    path("contact/", contact, name="contact"),
]
