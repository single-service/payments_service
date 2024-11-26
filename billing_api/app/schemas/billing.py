from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, condecimal


class OrderSchema(BaseModel):
    id: str
    payment_dt: Optional[datetime]
    status: int
    name: str
    price: condecimal(max_digits=11, decimal_places=2)
    currency: str
    is_subscription: bool
    items_count: int
    discount_value: int
    refunding_start_dt: Optional[datetime]
    refund_dt: Optional[datetime]
    refund_amount: condecimal(max_digits=11, decimal_places=2)
    fee: condecimal(max_digits=11, decimal_places=2)
    receipt_link: Optional[str]
    user_id: str
    user_email: Optional[str]

class OrdersSchema(BaseModel):
    count: int
    page: int
    limit: int
    orders: List[OrderSchema]

class RefundRequest(BaseModel):
    amount: condecimal(max_digits=11, decimal_places=2)


class CreateOrderRequest(BaseModel):
    payment_item_id: str
    items_count: int
    user_id: str
    user_email: str
    idempotent_key: str