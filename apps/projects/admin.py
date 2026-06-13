from django.contrib import admin

from .models import ProjectRequest


@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "email",
        "project_type",
        "budget_range",
        "timeline",
        "status",
        "is_spam",
        "created_at",
    )
    list_filter = ("status", "is_spam", "project_type", "budget_range", "timeline", "created_at")
    search_fields = ("full_name", "email", "company", "message")
    readonly_fields = ("created_at", "updated_at", "ip_address", "user_agent", "spam_reason")
    ordering = ("-created_at",)
