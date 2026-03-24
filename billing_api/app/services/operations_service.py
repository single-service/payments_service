from decimal import Decimal

from app.database_connector import get_async_session
from app.models import (Application, Order, PaymentItem, PaymentItemDiscount,
                        PaymentSystemParamter, OFDInterfaceParametr, FiscalDocument, Refund)
from fastapi import Depends
from sqlalchemy import desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class OperationsService:
    """Выполняет БД запросы для users_user"""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_operations(self, application_id, page, limit, status, user_id):
        query = select(Order).filter_by(application_id=application_id)
        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)
        # Пагинация
        query = query.offset((page - 1) * limit).limit(limit)
        groups = await self.session.execute(query)
        return groups.scalars().all()
    
    async def get_all_operations(self, application_id):
        query = select(Order).filter_by(application_id=application_id)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def get_operation(self, id):
        query = select(Order).filter_by(id=id)
        result = await self.session.execute(query)
        operation = result.scalar_one_or_none()
        if operation:
            await self.session.refresh(operation)
        return operation

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
        final_price = payment_item.price * items_count
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
        return final_price, amount, discount_value, discount_amount

    async def get_ofd_interface_parametres(self, application_id):
        query = select(OFDInterfaceParametr).filter_by(application_id=application_id)
        result = await self.session.execute(query)
        params = result.scalars().all()
        return {p.name: p.parameter_value for p in params}
    
    async def get_payment_system_parametres(self, application_id):
        query = select(PaymentSystemParamter).filter_by(application_id=application_id)
        result = await self.session.execute(query)
        params = result.scalars().all()
        return {p.name: p.parameter_value for p in params}
    
    async def create_fiscal_document(
        self, 
        id, 
        order_id, 
        refund_id,
        document_type, 
        data,
        created_dt,
        updated_dt
    ):
        new_fiscal_document = dict(
            id=id,
            order_id=order_id,
            refund_id=refund_id,
            document_type=document_type,
            request_payload=data,
            created_dt=created_dt,
            updated_dt=updated_dt
        )
        try:
            result = await self.session.execute(
                insert(FiscalDocument)
                .values(**new_fiscal_document)
                .returning(FiscalDocument.id)
            )
            new_id = result.scalar()
            await self.session.commit()
            return new_id
        except Exception as e:
            print(f"Create fiscal document Exception: {e}")
            return None
        
    async def update_fiscal_document(self, id: str, **kwargs):
        """
        Обновляет фискальный документ в базе данных.

        :param id: Идентификатор фискального документа
        :param kwargs: Ключи и значения полей, которые нужно обновить
        :return: Возвращает True, если обновление прошло успешно, иначе False
        """
        try:
            stmt = (
                update(FiscalDocument)
                .where(FiscalDocument.id == id)
                .values(kwargs)
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            print(f"Update fiscal document exception: {e}")
            return False
        return True

    async def create_order(self,
                           id: str,
                           created_dt,
                           updated_dt,
                           application_id,
                           payment_item_id,
                           payment_system,
                           status,
                           name,
                           price,
                           final_price,
                           currency,
                           is_subscription,
                           items_count,
                           discount_value,
                           user_id,
                           user_email,
                           idempotent_key,
                           amount,
                           discount_amount,
                           payment_system_order_id,
                           payment_link,
                           invoice_id,
                           is_subscription_first_order,
                           nomenclature=None,
                           ):
        new_order = dict(
            id=id,
            created_dt=created_dt,
            updated_dt=updated_dt,
            application_id=application_id,
            payment_item_id=payment_item_id,
            payment_system=payment_system,
            status=status,
            name=name,
            price=price,
            final_price=final_price,
            currency=currency,
            is_subscription=is_subscription,
            items_count=items_count,
            discount_value=discount_value,
            user_id=user_id,
            user_email=user_email,
            idempotent_key=idempotent_key,
            amount=amount,
            discount_amount=discount_amount,
            payment_system_order_id=payment_system_order_id,
            payment_link=payment_link,
            is_subscription_first_order=is_subscription_first_order,
            invoice_id=invoice_id,
            nomenclature=nomenclature
        )
        try:
            await self.session.execute(insert(Order).values(**new_order))
            await self.session.commit()
        except Exception as e:
            print(f"Create user Exception: {e}")
            return False
        return True

    async def update_order(self, id: str, **kwargs):
        """
        Обновляет заказ в базе данных.

        :param id: Идентификатор заказа
        :param kwargs: Ключи и значения полей, которые нужно обновить
        :return: Возвращает True, если обновление прошло успешно, иначе False
        """
        try:
            # Формирование запроса на обновление
            stmt = (
                update(Order)
                .where(Order.id == id)
                .values(kwargs)
            )

            # Выполнение обновления
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            print(f"Update order exception: {e}")
            return False
        return True
    
    async def get_amount_refunds(self, order_id):
        stmt = (
            select(func.coalesce(func.sum(Refund.amount), 0))
            .where(
                Refund.order_id == order_id,
                Refund.status == "done"
            )
        )
        result = await self.session.execute(stmt)
        refunded_amount = result.scalar_one()
        return refunded_amount
    
    async def get_order_refunds(self, order_id, **kwargs):
        limit = kwargs.pop("limit", None)
        page = kwargs.pop("page", None)
        query = select(Refund).filter_by(order_id=order_id)
        if limit and page:
            query = query.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_order_refunds_count(self, order_id: str):
        query = select(func.count()).select_from(Refund).filter_by(order_id=order_id)
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_order_refund(self, **kwargs):
        query = select(Refund).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_refund(self, **kwargs):
        try:
            await self.session.execute(
                insert(Refund)
                .values(**kwargs)
            )
            await self.session.commit()
        except Exception as e:
            print(f"Create refund Exception: {e}")
            return None
        
    async def update_order_refund(self, order_id, transaction_id, **kwargs):
        try:
            stmt = (
                update(Refund)
                .where(Refund.order_id == order_id, Refund.transaction_id == transaction_id)
                .values(**kwargs)
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            print(f"Update order exception: {e}")
            return False
        return True
    
    async def get_refunds_by_ids(self, order_ids: list, limit: int, page: int):
        if not order_ids:
            return []
        stmt = (
            select(Refund)
            .where(Refund.order_id.in_(order_ids))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_refunds_by_ids_count(self, order_ids: list):
        query = select(func.count()).select_from(Refund).where(Refund.order_id.in_(order_ids))
        result = await self.session.execute(query)
        return result.scalar()
