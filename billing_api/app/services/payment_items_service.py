from datetime import datetime, timedelta
import hashlib
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload
import jwt

from app.database_connector import get_async_session
from app.models import PaymentItemsGroup, PaymentItem, PaymentItemDiscount
from app.settings import settings


class PaymentItemsService:
    """Выполняет БД запросы для users_user"""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_groups(self, application_id):
        query = select(PaymentItemsGroup).filter_by(application_id=application_id)
        groups = await self.session.execute(query)
        return groups.scalars().all()


    async def get_payment_items(self, application_id, group_id=None):
        query = select(PaymentItem).filter_by(application_id=application_id)
        if group_id:
            query = query.filter_by(group_id=group_id)
        result = await self.session.execute(query)
        items = result.scalars().all()

        # Получаем все скидки для этих позиций
        item_ids = [item.id for item in items]  # Предположим, что у каждого PaymentItem есть уникальный id
        if item_ids:
            discounts_query = select(PaymentItemDiscount).filter(PaymentItemDiscount.payment_item_id.in_(item_ids))
            discounts_result = await self.session.execute(discounts_query)
            discounts = discounts_result.scalars().all()
            discount_map = {}
            for discount in discounts:
                if discount.payment_item_id not in discount_map:
                    discount_map[discount.payment_item_id] = []
                discount_map[discount.payment_item_id].append(discount)

            # Добавим скидки к соответствующим PaymentItem
            for item in items:
                item.discounts = discount_map.get(item.id, [])
        return items
