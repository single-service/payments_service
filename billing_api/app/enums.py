from enum import IntEnum

class OrderStatusChoices(IntEnum):
    CREATED = 1
    REJECTED = 2
    PAID = 3
    IS_REFUNDING = 4
    REFUNED = 5
    EXPIRED = 6
