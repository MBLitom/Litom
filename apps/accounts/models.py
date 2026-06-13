from django.conf import settings
from django.db import models


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_profile")
    full_name = models.CharField(max_length=160)
    company_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name or self.user.email or self.user.get_username()
