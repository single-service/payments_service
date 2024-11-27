from enum import IntEnum

from app.services.payment_systems import DummyPaymentSystemService, RobokassaPaymentSystemService

class OrderStatusChoices(IntEnum):
    CREATED = 1
    REJECTED = 2
    PAID = 3
    IS_REFUNDING = 4
    REFUNED = 5
    EXPIRED = 6


class PaymentSystemChoices(IntEnum):
    DUMMY = 1
    ROBOKASSA = 2
    YKASSA = 3

PAYMENT_SYSTEM_SERVICES_MAP = {
    PaymentSystemChoices.DUMMY: DummyPaymentSystemService,
    PaymentSystemChoices.ROBOKASSA: RobokassaPaymentSystemService,
    PaymentSystemChoices.YKASSA: None,
}