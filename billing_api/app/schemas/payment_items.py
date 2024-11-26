from typing import Optional, List

from pydantic import BaseModel, condecimal


class PaymentItemGroupSchema(BaseModel):
    id: str
    name: str


class PaymentItemDiscountSchema(BaseModel):
    id: str
    items_count: int
    discount_value: int


class PaymentItemSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]
    group_id: Optional[str]
    currency: str
    is_subscription: bool
    price: condecimal(max_digits=11, decimal_places=2)
    discounts: List[PaymentItemDiscountSchema]
