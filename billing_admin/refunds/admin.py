from django.contrib import admin
from unfold.admin import ModelAdmin

from refunds.models import Refund


@admin.register(Refund)
class RefundAdmin(ModelAdmin):
    list_display = [
        "order", "amount", "status", "created_dt"
    ]
    list_filter = ["status"]
    ordering = ('-created_dt',)
