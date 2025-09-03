from django.contrib import admin
from django.utils.translation import gettext as _

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Order, Expense


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "created_dt", "application", "status", "final_price", "currency", "is_subscription",
        "items_count", "discount_value", "payment_dt", "fee",
    ]
    ordering = ('-created_dt',)


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ["name", "expense_date", "amount",]
