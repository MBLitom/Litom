from django.db import models


class ProjectRequest(models.Model):
    class ProjectType(models.TextChoices):
        WEB_APPLICATION = "web_application", "Web application"
        CLIENT_PORTAL = "client_portal", "Client portal"
        INTERNAL_TOOL = "internal_tool", "Internal tool"
        ODOO_SYSTEM = "odoo_system", "Odoo system"
        AUTOMATION = "automation", "Automation workflow"
        API_INTEGRATION = "api_integration", "API integration"
        MOBILE_APPLICATION = "mobile_application", "Mobile application"
        PROJECT_RESCUE = "project_rescue", "Project rescue"
        OTHER = "other", "Other"

    class BudgetRange(models.TextChoices):
        UNDER_3000 = "under_3000", "Under 3,000 EUR"
        FROM_3000_TO_8000 = "3000_8000", "3,000-8,000 EUR"
        FROM_8000_TO_15000 = "8000_15000", "8,000-15,000 EUR"
        FROM_15000_TO_25000 = "15000_25000", "15,000-25,000 EUR"
        OVER_25000 = "over_25000", "Over 25,000 EUR"
        NOT_SURE = "not_sure", "Not sure"

    class Timeline(models.TextChoices):
        ASAP = "asap", "ASAP"
        ONE_TO_THREE_WEEKS = "1_3_weeks", "1-3 weeks"
        ONE_TO_TWO_MONTHS = "1_2_months", "1-2 months"
        THREE_PLUS_MONTHS = "3_plus_months", "3+ months"
        NOT_SURE = "not_sure", "Not sure"

    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        REJECTED = "rejected", "Rejected"
        CONVERTED = "converted", "Converted"

    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    company = models.CharField(max_length=160, blank=True)
    project_type = models.CharField(max_length=32, choices=ProjectType.choices)
    budget_range = models.CharField(max_length=32, choices=BudgetRange.choices)
    timeline = models.CharField(max_length=32, choices=Timeline.choices)
    message = models.TextField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=80, default="website_contact")
    is_spam = models.BooleanField(default=False)
    spam_reason = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.get_project_type_display()}"
