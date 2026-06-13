from django.contrib import admin

from .models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company_name", "phone", "user", "created_at")
    search_fields = ("full_name", "company_name", "phone", "user__email", "user__username")
    readonly_fields = ("created_at", "updated_at")
