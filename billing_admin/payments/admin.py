from django.contrib import admin
from django.utils.translation import gettext as _

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import PaymentItem, PaymentItemDiscount, PaymentItemsGroup


@admin.register(PaymentItem)
class PaymentItemAdmin(ModelAdmin):
    list_display = ["name", "application", "group", "price", "currency", "is_subscription"]


@admin.register(PaymentItemDiscount)
class PaymentItemDiscountAdmin(ModelAdmin):
    list_display = ["discount_value", "payment_item", "items_count"]


@admin.register(PaymentItemsGroup)
class PaymentItemsGroupAdmin(ModelAdmin):
    list_display = ["application", "name"]
