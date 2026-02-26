from enum import IntEnum

from app.services.payment_systems import (DummyPaymentSystemService,
                                          PayginePaymentSystemService,
                                          RobokassaPaymentSystemService)


class OrderStatusChoices(IntEnum):
    CREATED = 1
    REJECTED = 2
    PAID = 3
    IS_REFUNDING = 4
    REFUNED = 5
    EXPIRED = 6
    ERROR = 7
    UNKNOWN = 8

    @property
    def label(self):
        return {
            OrderStatusChoices.CREATED: "Создан",
            OrderStatusChoices.REJECTED: "Отклонён",
            OrderStatusChoices.PAID: "Оплачен",
            OrderStatusChoices.IS_REFUNDING: "В процессе возврата",
            OrderStatusChoices.REFUNED: "Возвращён",
            OrderStatusChoices.EXPIRED: "Истёк срок",
            OrderStatusChoices.ERROR: "Ошибка",
            OrderStatusChoices.UNKNOWN: "Неизвестно",
        }[self]


class PaymentSystemChoices(IntEnum):
    DUMMY = 1
    ROBOKASSA = 2
    YKASSA = 3
    PAYGINE = 4


PAYMENT_SYSTEM_SERVICES_MAP = {
    PaymentSystemChoices.DUMMY: DummyPaymentSystemService,
    PaymentSystemChoices.ROBOKASSA: RobokassaPaymentSystemService,
    PaymentSystemChoices.YKASSA: None,
    PaymentSystemChoices.PAYGINE: PayginePaymentSystemService,
}
