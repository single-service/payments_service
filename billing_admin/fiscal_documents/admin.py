from django.contrib import admin
from unfold.admin import ModelAdmin

from fiscal_documents.models import FiscalDocument


@admin.register(FiscalDocument)
class FiscalDocumentAdmin(ModelAdmin):
    list_display = [
        "created_dt", "order", "document_type", "status",
    ]
    list_filter = ["status", "document_type", "created_dt"]
    ordering = ('-created_dt',)
