from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FiscalDocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal_documents'
    verbose_name = _("Fiscal documents")
