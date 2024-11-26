from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, func, desc
from sqlalchemy.orm import selectinload
import jwt

from app.database_connector import get_async_session
from app.models import Order, Application, PaymentItem, PaymentItemDiscount
from app.settings import settings


class OperationsService:
    """Выполняет БД запросы для users_user"""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_operations(self, application_id, page, limit, status, user_id):
        query = select(Order).filter_by(application_id=application_id)
        if status:
            query = query.filter(status=status)
        if status:
            query = query.filter(user_id=user_id)
        # Пагинация
        query = query.offset((page - 1) * limit).limit(limit)
        groups = await self.session.execute(query)
        return groups.scalars().all()

    async def get_operation(self, id):
        query = select(Order).filter_by(id=id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_operations_count(self, application_id):
        query = select(func.count()).select_from(Order).filter_by(application_id=application_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def check_operation_created(self, application_id, idempotent_key):
        query = select(Order).filter_by(application_id=application_id, idempotent_key=idempotent_key)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_application(self, id):
        query = select(Application).filter_by(id=id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_payment_item(self, id):
        query = select(PaymentItem).filter_by(id=id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def calculate_prices(self, payment_item, items_count):
        print("===============")
        print("calculate_prices")
        final_price = payment_item.price * items_count
        print("final_price", final_price)
        # Создаем запрос на выборку скидок
        query = (
            select(PaymentItemDiscount)
            .filter(
                PaymentItemDiscount.payment_item_id == payment_item.id,
                PaymentItemDiscount.items_count >= items_count  # Условие сравнения
            )
            .order_by(desc(PaymentItemDiscount.items_count))  # Сортировка по убыванию
            .limit(1)  # Берем только первую запись
        )
        
        # Выполнение запроса
        result = await self.session.execute(query)
        discount_instance = result.scalars().first()  # Получаем первый объект или None
        discount_value = 0
        amount = final_price
        discount_amount = 0
        if discount_instance:
            discount_value = discount_instance.discount_value
            discount_amount = final_price * (Decimal(discount_value) / 100)
            amount -= discount_amount
        print("discount_value", discount_value)
        print("amount", amount)
        print("discount_amount", discount_amount)
        return final_price, amount, discount_value, discount_amount
