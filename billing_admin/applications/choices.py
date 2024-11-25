from django.db.models import IntegerChoices
from django.utils.translation import gettext as _

class PaymentSystemsChoices(IntegerChoices):
    DUMMY = 1, 'Dummy'
    ROBOKASSA = 2, 'ROBOKASSA'
    YKASSA = 3, 'YKASSA'
