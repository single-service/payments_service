from django.contrib import admin
from unfold.admin import ModelAdmin

from fiscal_documents.models import FiscalDocument

@admin.register(FiscalDocument)
class FiscalDocumentAdmin(ModelAdmin):
    list_display = [
        "order", "document_type", "status"
    ]
    ordering = ('-created_dt',)
