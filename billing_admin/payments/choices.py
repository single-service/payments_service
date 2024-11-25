from django.db.models import TextChoices
from django.utils.translation import gettext as _

class CurrencyChoices(TextChoices):
    RUB = 'RUB', _('Rubl')
    USD = 'USD', _('Dollar')
    EUR = 'EUR', _('EUR')
