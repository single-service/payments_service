from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.enums import (MeasureEnum, PaymentMethodEnum, PaymentTypeEnum, RefundStatus,
                       VatTypeEnum)
from pydantic import BaseModel, Field, condecimal


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
    refunding_start_dt: Optional[datetime] = None
    refund_dt: Optional[datetime] = None
    refund_amount: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    receipt_link: Optional[str]
    user_id: str
    user_email: Optional[str]


class OrdersSchema(BaseModel):
    count: int
    page: int
    limit: int
    orders: List[OrderSchema]


# class RefundRequest(BaseModel):
#     amount: condecimal(max_digits=11, decimal_places=2)


class CreateOrderRequest(BaseModel):
    payment_item_id: str
    items_count: int
    user_id: str
    user_email: Optional[str] = None
    idempotent_key: str


class NomenclatureModel(BaseModel):
    amount: Optional[int] = Field(
        None, ge=1, le=10000000000,
        description="[Необязательное] Общая стоимость позиции в копейках (целое число). Пример: 15000 = 150₽, 75050 = 750₽ 50коп"
    )
    count: float = Field(
        ..., gt=0,
        description="[Обязательное] Количество товара. Пример: 1.0, 2.5"
    )
    price: int = Field(
        ..., ge=1, le=10000000000,
        description="[Обязательное] Цена за 1 единицу в копейках. Пример: 7500 = 75₽, 150000 = 1500₽"
    )
    name: str = Field(
        ..., max_length=100,
        description="[Обязательное] Наименование товара/услуги. Максимум 100 символов"
    )
    nds: VatTypeEnum = Field(
        ...,
        description=(
            "[Обязательное] Ставка НДС. Допустимые значения: "
            "`none` — без НДС, "
            "`vat0` — НДС 0%, "
            "`vat5` — НДС 5%, "
            "`vat7` — НДС 7%, "
            "`vat10` — НДС 10%, "
            "`vat20` — НДС 20%, "
            "`vat22` — НДС 22%, "
            "`vat105` — расч. ставка 5/105, "
            "`vat107` — расч. ставка 7/107, "
            "`vat110` — расч. ставка 10/110, "
            "`vat120` — расч. ставка 20/120, "
            "`vat122` — расч. ставка 22/122"
        )
    )
    payment_method: PaymentMethodEnum = Field(
        ...,
        description=(
            "[Обязательное] Признак способа расчёта. Допустимые значения: "
            "`full_prepayment` — полная предоплата, "
            "`prepayment` — частичная предоплата, "
            "`advance` — аванс, "
            "`full_payment` — полный расчёт (самое частое), "
            "`partial_payment` — частичный расчёт и кредит, "
            "`credit` — передача в кредит, "
            "`credit_payment` — оплата кредита"
        )
    )
    measure: Optional[MeasureEnum] = Field(
        None,
        description=(
            "[Необязательное] Единица измерения (числовой код АТОЛ). Допустимые значения: "
            "`0` — без единицы измерения, "
            "`10` — г, `11` — кг, `12` — т, "
            "`20` — см, `21` — дм, `22` — м, "
            "`30` — см², `31` — дм², `32` — м², "
            "`40` — мл, `41` — л, `42` — м³, "
            "`50` — кВт·ч, `51` — Гкал, "
            "`70` — сутки, `71` — час, `72` — мин, `73` — с, "
            "`80` — Кб, `81` — Мб, `82` — Гб, `83` — Тб, "
            "`255` — иное"
        )
    )
    payment_type: Optional[PaymentTypeEnum] = Field(
        None,
        description=(
            "[Необязательное] Признак предмета расчёта. Допустимые значения: "
            "`commodity` — товар, "
            "`job` — работа, "
            "`service` — услуга, "
            "`payment` — платёж/аванс/предоплата"
        )
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 15000,
                "count": 2.0,
                "price": 7500,
                "name": "Товар А",
                "nds": "vat20",
                "payment_method": "full_payment",
                "measure": 22,
                "payment_type": "service",
            }
        }
    }


class CreateFreeOrderRequest(BaseModel):
    """
    Создание произвольного заказа (без привязки к payment_item).

    Все суммы указываются в **копейках** (целое число):
    - 10000 = 100₽
    - 15050 = 150₽ 50коп

    Поля `user_email` и `nomenclature` **обязательны** если у приложения включена фискализация.
    """
    amount: int = Field(
        ..., ge=1,
        description="[Обязательное] Сумма заказа в копейках. Пример: 10000 = 100₽, 15050 = 150₽ 50коп"
    )
    user_id: str = Field(..., description="[Обязательное] Идентификатор пользователя")
    user_email: Optional[str] = Field(
        None,
        description="[Необязательное, но обязательно при фискализации] Email пользователя для отправки чека"
    )
    idempotent_key: str = Field(
        ...,
        description="[Обязательное] Ключ идемпотентности — уникальная строка для предотвращения дублей. Повторный запрос с тем же ключом вернёт существующий заказ"
    )
    description: str = Field(..., description="[Обязательное] Описание заказа")
    currency: Optional[str] = Field(
        "RUB",
        description="[Необязательное] Валюта. По умолчанию RUB"
    )
    nomenclature: list[NomenclatureModel] = Field(
        [],
        description="[Необязательное, но обязательно при фискализации] Список товарных позиций для фискального чека"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 15000,
                "user_id": "user-123",
                "user_email": "user@example.com",
                "idempotent_key": "unique-key-001",
                "description": "Оплата услуг",
                "currency": "RUB",
                "nomenclature": [
                    {
                        "amount": 15000,
                        "count": 2.0,
                        "price": 7500,
                        "name": "Товар А",
                        "nds": "vat20",
                        "payment_method": "full_payment",
                        "measure": 22,
                        "payment_type": "service",
                    }
                ]
            }
        }
    }
    
    
class RefundRequest(BaseModel):
    amount: int = Field(
        ..., ge=1,
        description="[Обязательное] Сумма возврата в копейках. Пример: 10000 = 100₽, 15050 = 150₽ 50коп"
    )
    nomenclature: list[NomenclatureModel] = Field(
        [],
        description="[Необязательное, но обязательно при фискализации] Список товарных позиций для возврата"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 15000,
                "nomenclature": [
                    {
                        "amount": 15000,
                        "count": 2.0,
                        "price": 7500,
                        "name": "Товар А",
                        "nds": "vat20",
                        "payment_method": "full_payment",
                        "measure": 22,
                        "payment_type": "service",
                    }
                ]
            }
        }
    }


class RefundScheme(BaseModel):
    amount: int = Field(
        ..., ge=1,
        description="[Обязательное] Сумма возврата в копейках. Пример: 10000 = 100₽, 15050 = 150₽ 50коп"
    )
    nomenclature: list[NomenclatureModel] = Field(
        [],
        description="[Необязательное, но обязательно при фискализации] Список товарных позиций для возврата"
    )
    status: RefundStatus
    created_dt: datetime
