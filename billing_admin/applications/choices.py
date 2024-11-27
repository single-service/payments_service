from django.db.models import IntegerChoices
from django.utils.translation import gettext as _

class PaymentSystemsChoices(IntegerChoices):
    DUMMY = 1, 'Dummy'
    ROBOKASSA = 2, 'ROBOKASSA'
    YKASSA = 3, 'YKASSA'


PAYMENT_SYSTEM_PARAMETERS_MAP = {
    PaymentSystemsChoices.DUMMY: ["HOST"],
    PaymentSystemsChoices.ROBOKASSA: ["ROBOKASSA_LOGIN", "ROBOKASSA_PASSWORD_1", "ROBOKASSA_PASSWORD_2", "ROBOKASSA_TEST", ],
    PaymentSystemsChoices.YKASSA: [],
}