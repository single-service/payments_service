from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException

from app.schemas.billing import OrdersSchema, RefundRequest, CreateOrderRequest
from app.utils.auth import TokenAuth
from app.services.operations_service import OperationsService
from app.enums import OrderStatusChoices


router = APIRouter()


@router.get(
    '/operations/',
    response_model=OrdersSchema,
    include_in_schema=True,
)
async def get_live(
    application_id=Depends(TokenAuth),
    operations_service = Depends(OperationsService),
    limit: int = Query(50, description="Limit"),
    page: int = Query(1, description="Page"),
    status: int = Query(None, description="Status"),
    user_id: str = Query(None, description="Status"),
):
    """Список операций"""
    cnt = await operations_service.get_operations_count(application_id)
    orders = await operations_service.get_operations(
        application_id=application_id,
        limit=limit,
        page=page,
        status=status,
        user_id=user_id
    )
    result = {
        "count": cnt,
        "limit": 50,
        "page": 1,
        "orders": orders
    }
    return result


@router.post("/operations/{operation_id}/refund")
async def refund_order(
    operation_id: str,
    refund_request: RefundRequest,
    application_id=Depends(TokenAuth),
): 
    # Пока эндпоинт в разработке, можно вернуть ошибку 400 с сообщением
    raise HTTPException(
        status_code=400,
        detail="This endpoint is under development"
    )

@router.post("/operations/{operation_id}/cancel")
async def cancel_order(
    operation_id: str,
    application_id=Depends(TokenAuth),
): 
    # Пока эндпоинт в разработке, можно вернуть ошибку 400 с сообщением
    raise HTTPException(
        status_code=400,
        detail="This endpoint is under development"
    )

@router.post("/operations/")
async def refund_order(
    create_body: CreateOrderRequest,
    application_id=Depends(TokenAuth),
    operations_service = Depends(OperationsService),
): 
    # Проверка что такая операция уже создана
    operation_exist = await operations_service.check_operation_created(
        application_id=application_id,
        idempotent_key=create_body.idempotent_key
    )
    if operation_exist:
        raise HTTPException(
            status_code=400,
            detail="Operation created yet"
        )
    # Проверка items_count 
    if create_body.items_count <= 0:
        raise HTTPException(
            status_code=400,
            detail="Items count need to be grater then 0"
        )
    payment_item = await operations_service.get_payment_item(create_body.payment_item_id)
    if not payment_item:
        raise HTTPException(
            status_code=400,
            detail="Wrong payment item"
        )
    if payment_item.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="You couldn't pay this item"
        )

    # Подтягиваем application получаем недостающие данные
    application = await operations_service.get_application(application_id)
    final_price, amount, discount_value, discount_amount = await operations_service.calculate_prices(payment_item, create_body.items_count)
    payload = dict(
        application_id=application_id,
        payment_item_id=create_body.payment_item_id,
        payment_system=application.payment_system,
        status=OrderStatusChoices.CREATED,
        name=payment_item.name,
        price=payment_item.price,
        final_price=final_price,
        currency=payment_item.currency,
        is_subscription=payment_item.is_subscription,
        items_count=create_body.items_count,
        discount_value=discount_value,
        user_id=create_body.user_id,
        user_email=create_body.user_email,
        idempotent_key=create_body.idempotent_key,
        amount=amount,
        discount_amount=discount_amount,
        payment_system_order_id=0, # рассчитать
    )
    # Получаем ссылку
    
    return payload