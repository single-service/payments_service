from enum import IntEnum, Enum

from app.services.payment_systems import (DummyPaymentSystemService,
                                          PayginePaymentSystemService,
                                          RobokassaPaymentSystemService)
from app.services.fiscal_services import AtolService


class OrderStatusChoices(IntEnum):
    CREATED = 1
    REJECTED = 2
    PAID = 3
    IS_REFUNDING = 4
    REFUNED = 5
    EXPIRED = 6
    ERROR = 7
    UNKNOWN = 8
    PARTIALLY_REFUNDED = 9

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
    
    
class OFDInterfaceChoices(IntEnum):
    ATOL = 1
    
    
class DocumentType(Enum):
    SALE = "sale"
    REFUND = "refund"
    
    
class MeasureEnum(int, Enum):
    NONE = 0
    GRAM = 10
    KILOGRAM = 11
    TON = 12
    CENTIMETER = 20
    DECIMETER = 21
    METER = 22
    SQUARE_CM = 30
    SQUARE_DM = 31
    SQUARE_M = 32
    MILLILITER = 40
    LITER = 41
    CUBIC_M = 42
    KWH = 50
    GIGACAL = 51
    DAY = 70
    HOUR = 71
    MINUTE = 72
    SECOND = 73
    KB = 80
    MB = 81
    GB = 82
    TB = 83
    OTHER = 255


class VatTypeEnum(str, Enum):
    NONE = "none"
    VAT0 = "vat0"
    VAT10 = "vat10"
    VAT110 = "vat110"
    VAT20 = "vat20"
    VAT120 = "vat120"
    VAT5 = "vat5"
    VAT7 = "vat7"
    VAT105 = "vat105"
    VAT107 = "vat107"
    VAT22 = "vat22"
    VAT122 = "vat122"
    
    
class RefundStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class PaymentMethodEnum(str, Enum):
    FULL_PREPAYMENT = "full_prepayment"
    PREPAYMENT = "prepayment"
    ADVANCE = "advance"
    FULL_PAYMENT = "full_payment"
    PARTIAL_PAYMENT = "partial_payment"
    CREDIT = "credit"
    CREDIT_PAYMENT = "credit_payment"
    
    
class PaymentTypeEnum(str, Enum):
    PRODUCT = "commodity"
    WORK = "job"
    SERVICE = "service"
    PAYMENT = "payment"


PAYMENT_SYSTEM_SERVICES_MAP = {
    PaymentSystemChoices.DUMMY: DummyPaymentSystemService,
    PaymentSystemChoices.ROBOKASSA: RobokassaPaymentSystemService,
    PaymentSystemChoices.YKASSA: None,
    PaymentSystemChoices.PAYGINE: PayginePaymentSystemService,
}

OFD_INTERFACE_SERVICE_MAP = {
    OFDInterfaceChoices.ATOL: AtolService
}
