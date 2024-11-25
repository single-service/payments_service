from django.db.models import IntegerChoices
from django.utils.translation import gettext as _

class CurrencyChoices(IntegerChoices):
    CREATED = 1, _('Created')
    REJECTED = 2, _('Rejected')
    PAID = 3, _('Paid')
    IS_REFUNDING = 4, _("Is refunding")
    REFUNED = 5, _("Refuned")
    EXPIRED = 6, _("Expired")
