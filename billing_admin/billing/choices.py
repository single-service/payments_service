from django.db.models import IntegerChoices
from django.utils.translation import gettext as _

class StatusChoices(IntegerChoices):
    CREATED = 1, _('Created')
    REJECTED = 2, _('Rejected')
    PAID = 3, _('Paid')
    IS_REFUNDING = 4, _("Is refunding")
    REFUNED = 5, _("Refuned")
    EXPIRED = 6, _("Expired")
    ERROR = 7, _("Error")
    UNKNOWN = 8, _("Unknown")
