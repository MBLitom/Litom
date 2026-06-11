from django.urls import path

from .views import healthcheck

app_name = "core"

urlpatterns = [
    path("", healthcheck, name="healthcheck"),
]
