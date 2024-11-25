from django.contrib import admin
from django.utils.translation import gettext as _

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "created_dt", "application", "status", "price", "currency", "is_subscription",
        "items_count", "discount_value", "payment_dt", "fee",
        "refund_dt", "refund_amount"
    ]
