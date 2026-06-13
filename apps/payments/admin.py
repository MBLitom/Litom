from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import PaymentEvent, ProjectReviewOrder


@admin.register(ProjectReviewOrder)
class ProjectReviewOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "email", "amount_display", "status", "created_at", "paid_at")
    list_filter = ("status", "currency", "created_at", "paid_at")
    search_fields = ("order_number", "email", "company", "full_name", "short_description")
    readonly_fields = ("order_number", "paysera_request_data", "paysera_callback_data", "paid_at", "created_at", "updated_at")
    ordering = ("-created_at",)

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return f"{obj.amount_cents / 100:.2f} {obj.currency}"


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ("order_link", "provider", "event_type", "verified", "created_at")
    list_filter = ("provider", "event_type", "verified", "created_at")
    search_fields = ("order__order_number", "event_type")
    readonly_fields = ("order", "provider", "event_type", "raw_data", "verified", "created_at")
    ordering = ("-created_at",)

    @admin.display(description="Order")
    def order_link(self, obj):
        if not obj.order_id:
            return "-"
        url = reverse("admin:payments_projectrevieworder_change", args=[obj.order_id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
