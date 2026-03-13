from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, condecimal, confloat, conint

from app.enums import PaymentMethodEnum, VatTypeEnum, MeasureEnum, PaymentTypeEnum


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
    user_email: Optional[str] = None
    idempotent_key: str
    
    
class NomenclatureModel(BaseModel):
    amount: Optional[int] = Field(
        None, ge=1, le=100000000, description="Общая стоимость товара в товарной позиции"
    )
    count: float = Field(..., gt=0, description="Количество")
    price: int = Field(
        ..., ge=1, le=100000000, description="Цена в копейках (за 1 единицу)"
    )
    name: str = Field(
        ..., max_length=100, description="Наименование"
    )
    nds: VatTypeEnum = Field(..., description="Ставка НДС")
    payment_method: PaymentMethodEnum = Field(
        ..., description="Признак способа расчета"
    )
    measure: Optional[MeasureEnum] = Field(
        None, description="Единица измерения количества предмета"
    )
    payment_type: Optional[PaymentTypeEnum] = Field(
        None, description="Признак предмета расчета"
    )

    class Config:
        schema_extra = {
            "example": {
                "amount": 15000,
                "count": 2.0,
                "price": 7500,
                "name": "Товар А",
                "nds": "vat20",
                "payment_method": "full_payment",
                "measure": 22,
                "payment_type": 1,
            }
        }


class CreateFreeOrderRequest(BaseModel):
    amount: condecimal(max_digits=11, decimal_places=2)
    user_id: str
    user_email: Optional[str] = None
    idempotent_key: str
    description: str
    currency: Optional[str] = "RUB"
    nomenclature: list[NomenclatureModel] = []