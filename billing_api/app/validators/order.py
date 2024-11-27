from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.operations_service import OperationsService
from app.enums import PAYMENT_SYSTEM_SERVICES_MAP
from app.database_connector import get_async_session


async def validate_create_order(application_id, idempotent_key, items_count, payment_item_id, operations_service):
    # Проверка что такая операция уже создана
    operation_exist = await operations_service.check_operation_created(
        application_id=application_id,
        idempotent_key=idempotent_key
    )
    if operation_exist:
        return None, "Operation created yet"
    # Проверка items_count 
    if items_count <= 0:
        return None, "Items count need to be grater then 0"
    payment_item = await operations_service.get_payment_item(payment_item_id)
    if not payment_item:
        return None, "Wrong payment item"
    if payment_item.price <= 0:
        return None, "You couldn't pay this item"
    application = await operations_service.get_application(application_id)
    payment_service_cls = PAYMENT_SYSTEM_SERVICES_MAP.get(application.payment_system)
    if not payment_service_cls:
        return None, "This payment system is not ready"
    validated_data = {
        "payment_item": payment_item,
        "application": application,
        "payment_service_cls": payment_service_cls
    }
    return validated_data, None
