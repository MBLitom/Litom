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
        "status",
        "created_at",
    )
    list_filter = ("status", "project_type", "budget_range", "timeline", "created_at")
    search_fields = ("full_name", "email", "company", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
