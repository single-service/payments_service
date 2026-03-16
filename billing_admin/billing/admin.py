from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from fiscal_documents.models import FiscalDocument
from .models import Order, Expense


class FiscalDocumentInline(TabularInline):
    model = FiscalDocument
    extra = 0
    readonly_fields = ["created_dt", "document_type", "status", "fiscal_link", "error"]
    fields = ["created_dt", "document_type", "status", "fiscal_link", "error"]
    can_delete = False
    show_change_link = True

    def fiscal_link(self, obj):
        if obj.pk:
            url = reverse("admin:fiscal_documents_fiscaldocument_change", args=[obj.pk])
            return format_html('<a href="{}">Открыть чек</a>', url)
        return "-"
    fiscal_link.short_description = "Чек"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "created_dt", "application", "status", "final_price", "currency", "is_subscription",
        "items_count", "discount_value", "payment_dt", "fee",
    ]
    ordering = ('-created_dt',)
    inlines = [FiscalDocumentInline]


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ["name", "expense_date", "amount",]
