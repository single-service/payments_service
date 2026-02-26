from django.db.models import IntegerChoices
from django.utils.translation import gettext as _

class PaymentSystemsChoices(IntegerChoices):
    DUMMY = 1, 'Dummy'
    ROBOKASSA = 2, 'ROBOKASSA'
    YKASSA = 3, 'YKASSA'
    PAYGINE = 4, 'PAYGINE'


class SnoChoices(IntegerChoices):
    OSN = 1, 'Общая СН'
    USN6 = 2, 'Упрощенная СН (доходы)'
    USN15 = 3, 'Упрощенная СН (доходы минус расходы)'
    ESHN = 4, 'Единый сельскохозяйственный налог'
    PATENT = 5, 'Патентная СН'


class TaxChoices(IntegerChoices):
    NO_NDS = 1, "Без НДС"
    vat0 = 2, "НДС по ставке 0%"
    vat10 = 3, "НДС чека по ставке 10%"
    vat110 = 4, "НДС чека по расчетной ставке 10/110"
    vat20 = 5, "НДС чека по ставке 20%"
    vat120 = 7, "НДС чека по расчетной ставке 20/120"
    vat5 = 8, "НДС по ставке 5%"
    vat7 = 9, "НДС по ставке 7%"
    vat105 = 10, "НДС чека по расчетной ставке 5/105"
    vat107 = 11, "НДС чека по расчетной ставке 7/107"


PAYMENT_SYSTEM_PARAMETERS_MAP = {
    PaymentSystemsChoices.DUMMY: ["HOST"],
    PaymentSystemsChoices.ROBOKASSA: ["ROBOKASSA_LOGIN", "ROBOKASSA_PASSWORD_1", "ROBOKASSA_PASSWORD_2", "ROBOKASSA_TEST", ],
    PaymentSystemsChoices.YKASSA: [],
    PaymentSystemsChoices.PAYGINE: ["PAYGINE_SECTOR", "PAYGINE_SIGN_PASSWORD", "PAYGINE_BASE_URL"],
}
