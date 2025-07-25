from datetime import datetime
from typing import Annotated
import uuid

import aiohttp
from fastapi import APIRouter, Depends, Query, HTTPException, Request, Path, BackgroundTasks

from app.schemas.billing import OrdersSchema, RefundRequest, CreateOrderRequest
from app.utils.auth import TokenAuth
from app.services.operations_service import OperationsService
from app.enums import OrderStatusChoices, PAYMENT_SYSTEM_SERVICES_MAP
from app.validators.order import validate_create_order


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
async def create_order(
    create_body: CreateOrderRequest,
    application_id=Depends(TokenAuth),
    operations_service = Depends(OperationsService),
):
    # Валидация
    validated_data, error = await validate_create_order(
        application_id=application_id,
        idempotent_key=create_body.idempotent_key,
        items_count=create_body.items_count,
        payment_item_id=create_body.payment_item_id,
        operations_service=operations_service,
    )
    if error:
        if error == "Operation created yet":
            operation = validated_data["operation"]
            return operation
        else:
            raise HTTPException(
                status_code=400,
                detail=error
            )
    application = validated_data["application"]
    payment_item = validated_data["payment_item"]
    payment_service_cls = validated_data["payment_service_cls"]
    
    # Подтягиваем application получаем недостающие данные
    final_price, amount, discount_value, discount_amount = await operations_service.calculate_prices(payment_item, create_body.items_count)
    payment_system_parametres = await operations_service.get_payment_system_parametres(application_id)
    payment_service = payment_service_cls()
    payment_service.set_system_parameters(**payment_system_parametres)
    operation_id = str(uuid.uuid4())
    is_subscription_first_order = True if payment_item.is_subscription else None
    nomenclature = None
    if application.is_fiscalisation:
        base_items = [
            {
                "name": payment_item.name,
                "cost": payment_item.price,
                "count": create_body.items_count,
                "amount": amount,
            }
        ]
        nomenclature = payment_service.get_nomenclature(
            base_sno=application.sno,
            base_nds=application.tax,
            base_items=base_items,
        )
    # Получаем ссылку
    link = payment_service.create_link(
        final_amount=amount,
        user_email=create_body.user_email,
        description=payment_item.description,
        payment_id=payment_item.id,
        operation_id=operation_id,
        is_subscription=payment_item.is_subscription,
        nomenclature=nomenclature
    )
    # Добавляем операцию
    payload = dict(
        id=operation_id,
        created_dt=datetime.now(),
        updated_dt=datetime.now(),
        invoice_id="",
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
        payment_system_order_id=None,
        payment_link=link,
        is_subscription_first_order=is_subscription_first_order,
    )
    create_status = await operations_service.create_order(**payload)
    if not create_status:
        raise HTTPException(
            status_code=400,
            detail="Order create failed"
        )
    return payload

async def perform_callback(application_callback_url: str, payload: dict):
    """Выполняет асинхронный POST-запрос."""
    headers = {'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(application_callback_url, json=payload, headers=headers) as resp:
            return await resp.text()


@router.post("/order/payment/{payment_method}/")
async def payment_callback(
    background_tasks: BackgroundTasks,
    request: Request,
    payment_method: Annotated[str, Path(title="Payment method")],
    operations_service = Depends(OperationsService),
):
    """
    Колбэк-платежный эндпоинт для приема уведомлений о платежах.
    
    :param request: объект запроса, содержащий заголовки и тело
    :param payment_method: строка, идентифицирующая используемый метод оплаты
    """
    print("payment_method", payment_method)
    try:
        payment_service_cls = PAYMENT_SYSTEM_SERVICES_MAP.get(int(payment_method))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Technical Error"
        )
    if not payment_service_cls:
        raise HTTPException(
            status_code=400,
            detail="This payment system is not ready"
        )
    print("payment_service_cls", payment_service_cls)
    
    # Чтение тела запроса
    body = await request.body()
    payload = body.decode()
    payment_service = payment_service_cls()
    data = payment_service.prepare_payload(payload)
    print("========")
    print("Data: ", data)
    operation = await operations_service.get_operation(data["operation_id"])
    if not operation:
        raise HTTPException(
            status_code=400,
            detail="Wrong operation"
        )
    payment_system_parametres = await operations_service.get_payment_system_parametres(operation.application_id)
    payment_service.set_system_parameters(**payment_system_parametres)
    error = payment_service.check_payment(operation, data)
    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )
    update_fields = [
        "payment_dt", "status", "fee", "invoice_id",
        "receipt_link", "crc",
    ]
    update_data = {field_name: data.get(field_name) for field_name in update_fields}
    await operations_service.update_order(data['operation_id'], **update_data)

    # Подготовка callback
    payload = {
        "operation_id": operation.id,
        "invoice_id": operation.invoice_id,
        "final_price": float(operation.final_price),
        "discount_amount": float(operation.discount_amount),
        "user_id": operation.user_id,
        "receipt_link": operation.receipt_link,
        "fee": operation.fee,
        "currency": operation.currency,
    }
    application = await operations_service.get_application(operation.application_id)
    if application.callback_url:
        background_tasks.add_task(perform_callback, application.callback_url, payload)
    return {"detail": "OK"}
