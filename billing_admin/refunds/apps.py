from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RefundsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'refunds'
    verbose_name = _("Refunds")
