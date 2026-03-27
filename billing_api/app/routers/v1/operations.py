import asyncio
import json
import uuid
from datetime import datetime
from typing import Annotated

import aiohttp
from fastapi.responses import StreamingResponse
from app.enums import OFD_INTERFACE_SERVICE_MAP, PAYMENT_SYSTEM_SERVICES_MAP, OrderStatusChoices
from app.schemas.billing import (CreateFreeOrderRequest, CreateOrderRequest,
                                 OrdersSchema, RefundRequest, RefundResonseSchema)
from app.services.operations_service import OperationsService
from app.utils.auth import TokenAuth
from app.validators.order import validate_create_order
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Path,
                     Query, Request)
from app.services.fiscal_services import AtolService
from app.logger import get_logger
from app.validators.refunds import validate_refund_nomenclature

logger = get_logger()
router = APIRouter()


@router.post("/callback/")
async def debug_callback(request: Request):
    """Тестовый эндпоинт для проверки исходящего колбэка."""
    body = await request.json()
    print("=== CALLBACK RECEIVED ===")
    print(body)
    print("=========================")
    return {"detail": "OK"}


@router.get(
    '/operations/',
    response_model=OrdersSchema,
    include_in_schema=True,
)
async def get_live(
    application_id=Depends(TokenAuth),
    operations_service=Depends(OperationsService),
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


@router.get(
    "/operations/{operation_id}/status",
    summary="Получение статуса операции",
    description="""
Получение текущего статуса операции по её уникальному идентификатору (SSE).
Отправляет новый статус операции при его изменении.

**Возвращаемый объект:**

```
{
    "data": <status>
}
```

**Статусы операции (status) могут быть следующими:**

| status | Описание            |
| ------ | ------------------- |
| 1      | Создан              |
| 2      | Отклонён            |
| 3      | Оплачен             |
| 4      | В процессе возврата |
| 5      | Возвращён           |
| 6      | Истёк срок          |
| 7      | Ошибка              |
| 8      | Неизвестно          |

    """
)
async def order_status(
    operation_id: str,
    operations_service=Depends(OperationsService),
) -> StreamingResponse:

    async def operation_status_generator(
        operation_id: str,
        operations_service: OperationsService,
        interval: int = 5
    ):
        last_status = None
        while True:
            try:
                operation = await operations_service.get_operation(operation_id)
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                break

            if not operation:
                yield f"event: error\ndata: {json.dumps({'error': 'Operation not found'})}\n\n"
                break

            current_status = operation.status
            print(last_status, current_status)
            if current_status != last_status:
                last_status = current_status
                yield f"data: {json.dumps({'data': current_status})}\n\n"
            else:
                yield ":\n\n"

            await asyncio.sleep(interval)

    generator = operation_status_generator(
        operation_id=operation_id,
        operations_service=operations_service,
        interval=5
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/operations/{operation_id}/refund")
async def refund_order(
    operation_id: str,
    refund_request: RefundRequest,
    application_id=Depends(TokenAuth),
    operations_service=Depends(OperationsService),
):
    operation = await operations_service.get_operation(operation_id)
    if not operation:
        logger.error(f"refund: operation not found {operation_id=}")
        raise HTTPException(
            status_code=400,
            detail="Wrong operation"
        )
    if operation.application_id != application_id:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    if operation.status == OrderStatusChoices.REFUNED:
        raise HTTPException(
            status_code=400,
            detail="The operation is non-refundable."
        )
    application = await operations_service.get_application(application_id)
    order_nomenclature = operation.nomenclature or []
    if not order_nomenclature and application.is_fiscalisation:
        raise HTTPException(400, "Operation has no nomenclature")
    if application.is_fiscalisation:
        await validate_refund_nomenclature(
            operation,
            refund_request,
            operations_service
        )
    amount_refunds = await operations_service.get_amount_refunds(operation.id)
    if refund_request.amount + amount_refunds > operation.final_price:
        raise HTTPException(
            status_code=400,
            detail="The amount of refunds exceeds the order amount."
        )
        
    payment_service_cls = PAYMENT_SYSTEM_SERVICES_MAP.get(operation.payment_system)
    if not payment_service_cls:
        logger.error(f"refund: payment system not ready payment_system={operation.payment_system}")
        raise HTTPException(status_code=400, detail="This payment system is not ready")

    payment_system_parametres = await operations_service.get_payment_system_parametres(application_id)
    payment_service = payment_service_cls()
    payment_service.set_system_parameters(**payment_system_parametres)
        
    try:
        transaction_id = await payment_service.refund(operation, refund_request.amount)
        await operations_service.update_order(
            operation_id,
            status=OrderStatusChoices.IS_REFUNDING
        )
        await operations_service.create_refund(
            id=str(uuid.uuid4()),
            order_id=operation_id,
            amount=refund_request.amount,
            status="pending",
            nomenclature=[item.model_dump() for item in refund_request.nomenclature],
            transaction_id=transaction_id,
            updated_dt=datetime.now(),
            created_dt=datetime.now(),
        )
        return {"status": "success"}
    except Exception as exc:
        logger.error(f"{exc}")
        raise HTTPException(status_code=400, detail="Error refund")
    

@router.get(
    "/operations/refunds",
    response_model=RefundResonseSchema,
    description="""
Получение списка возвратов.
При передаче в параметрах запроса operation_id будет возвращен список возвратов по операции.

**Статусы возвратов (status) могут быть следующими:**

| status    | Описание            |
| --------- | ------------------- |
| pending   | В обработке         |
| failed    | Отклонён            |
| done      | Успешно             |

    """
)    
async def get_refunds(
    operation_id: str = None,
    limit: int = Query(50, description="Limit"),
    page: int = Query(1, description="Page"),
    application_id=Depends(TokenAuth),
    operations_service=Depends(OperationsService),
):
    """
    Получение возвратов.
    - Если передан operation_id, возвращаются возвраты по конкретной операции
    - Иначе возвращаются все возвраты по всем заказам пользователя (application_id)
    """
    if not operation_id:
        operations = await operations_service.get_all_operations(application_id)
        order_ids = [op.id for op in operations]
        refunds = await operations_service.get_refunds_by_ids(order_ids, limit, page)
        cnt = await operations_service.get_refunds_by_ids_count(order_ids)
        return {
            "count": cnt,
            "limit": limit,
            "page": page,
            "refunds": refunds
        }
    operation = await operations_service.get_operation(operation_id)
    if not operation:
        logger.error(f"refund: operation not found {operation_id=}")
        raise HTTPException(
            status_code=400,
            detail="Wrong operation"
        )
    if operation.application_id != application_id:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )
    refunds = await operations_service.get_order_refunds(
        operation_id, 
        limit=limit, 
        page=page
    )
    cnt = await operations_service.get_order_refunds_count(
        operation_id
    )
    return {
        "count": cnt,
        "limit": limit,
        "page": page,
        "refunds": refunds
    }


@router.post("/operations/")
async def create_order(
    create_body: CreateOrderRequest,
    application_id=Depends(TokenAuth),
    operations_service=Depends(OperationsService),
):
    logger.info(
        f"create_order: application_id={application_id} payment_item_id={create_body.payment_item_id} idempotent_key={create_body.idempotent_key}")
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
            logger.info(f"create_order: idempotent hit, returning existing operation={operation.id}")
            return operation
        else:
            logger.warning(f"create_order: validation error={error} application_id={application_id}")
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
        logger.info(
            f"create_order: fiscalisation enabled for application_id={application_id} operation_id={operation_id}")
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
    logger.info(f"create_order: payment link created operation_id={operation_id} amount={amount}")
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
        nomenclature=nomenclature,
    )
    create_status = await operations_service.create_order(**payload)
    if not create_status:
        logger.error(f"create_order: failed to save operation_id={operation_id} application_id={application_id}")
        raise HTTPException(
            status_code=400,
            detail="Order create failed"
        )
    logger.info(f"create_order: success operation_id={operation_id} amount={amount} user_id={create_body.user_id}")
    return payload


@router.post(
    "/operations/free/",
    summary="Создание произвольного заказа",
    description="""
Создаёт заказ с произвольной суммой (без привязки к payment_item).

**Все суммы указываются в копейках:**
- `10000` = 100₽
- `15050` = 150₽ 50коп

**Обязательные поля:** `amount`, `user_id`, `idempotent_key`, `description`

**При включённой фискализации** дополнительно обязательны: `user_email`, `nomenclature` (минимум одна позиция)

**Идемпотентность:** повторный запрос с тем же `idempotent_key` вернёт существующий заказ без создания нового.

---

**Поля номенклатуры (`nomenclature[]`):**

| Поле | Обяз. | Описание |
|------|-------|----------|
| `name` | ✅ | Наименование товара/услуги (макс. 100 символов) |
| `price` | ✅ | Цена за 1 единицу в копейках |
| `count` | ✅ | Количество |
| `nds` | ✅ | Ставка НДС: `none`, `vat0`, `vat5`, `vat7`, `vat10`, `vat20`, `vat22`, `vat105`, `vat107`, `vat110`, `vat120`, `vat122` |
| `payment_method` | ✅ | Способ расчёта: `full_prepayment`, `prepayment`, `advance`, `full_payment`, `partial_payment`, `credit`, `credit_payment` |
| `amount` | ❌ | Общая стоимость позиции в копейках (если не указано — `price * count`) |
| `measure` | ❌ | Единица измерения (код): `0`-без, `11`-кг, `22`-м, `41`-л, `71`-час, `255`-иное |
| `payment_type` | ❌ | Предмет расчёта: `commodity`, `job`, `service`, `payment` |
""",
)
async def create_free_order(
    create_body: CreateFreeOrderRequest,
    application_id=Depends(TokenAuth),
    operations_service=Depends(OperationsService),
):
    logger.info(f"create_free_order: application_id={application_id} data={create_body}")
    # Идемпотентность
    operation_exist = await operations_service.check_operation_created(
        application_id=application_id,
        idempotent_key=create_body.idempotent_key,
    )
    if operation_exist:
        logger.info(f"create_free_order: idempotent hit, returning existing operation={operation_exist.id}")
        return operation_exist

    application = await operations_service.get_application(application_id)
    if application.is_fiscalisation and (not create_body.user_email or not create_body.nomenclature):
        logger.warning(
            f"create_free_order: fiscalisation enabled but email/nomenclature missing application_id={application_id}")
        raise HTTPException(
            status_code=422,
            detail="When fiscalizing, you must fill in the user's email address and product code."
        )
    payment_service_cls = PAYMENT_SYSTEM_SERVICES_MAP.get(application.payment_system)
    if not payment_service_cls:
        logger.error(
            f"create_free_order: payment system not ready payment_system={application.payment_system} application_id={application_id}")
        raise HTTPException(status_code=400, detail="This payment system is not ready")

    payment_system_parametres = await operations_service.get_payment_system_parametres(application_id)
    payment_service = payment_service_cls()
    payment_service.set_system_parameters(**payment_system_parametres)

    operation_id = str(uuid.uuid4())
    amount_rubles = create_body.amount / 100
    link, order_id = payment_service.create_link(
        final_amount=amount_rubles,
        user_email=create_body.user_email,
        description=create_body.description,
        payment_id=operation_id,
        operation_id=operation_id,
    )
    if not link:
        logger.error(f"create_free_order: failed to create payment link operation_id={operation_id}")
        raise HTTPException(status_code=400, detail="Payment system unavailable, failed to create payment link")
    logger.info(f"create_free_order: payment link created operation_id={operation_id} body={create_body}")

    payload = dict(
        id=operation_id,
        created_dt=datetime.now(),
        updated_dt=datetime.now(),
        invoice_id="",
        application_id=application_id,
        payment_item_id=None,
        payment_system=application.payment_system,
        status=OrderStatusChoices.CREATED,
        name=create_body.description or "",
        price=create_body.amount,
        final_price=create_body.amount,
        currency=create_body.currency,
        is_subscription=False,
        items_count=1,
        discount_value=0,
        user_id=create_body.user_id,
        user_email=create_body.user_email,
        idempotent_key=create_body.idempotent_key,
        amount=create_body.amount,
        discount_amount=0,
        payment_system_order_id=order_id,
        payment_link=link,
        is_subscription_first_order=None,
        nomenclature=[item.model_dump() for item in create_body.nomenclature],
        additional_data=create_body.additional_data,
    )

    create_status = await operations_service.create_order(**payload)
    if not create_status:
        logger.error(f"create_free_order: failed to save operation_id={operation_id} application_id={application_id}")
        raise HTTPException(status_code=400, detail="Order create failed")
    logger.info(
        f"create_free_order: success operation_id={operation_id} amount={create_body.amount} user_id={create_body.user_id}")
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
    operations_service=Depends(OperationsService),
):
    """
    Колбэк-платежный эндпоинт для приема уведомлений о платежах.

    :param request: объект запроса, содержащий заголовки и тело
    :param payment_method: строка, идентифицирующая используемый метод оплаты
    """
    body = await request.body()
    logger.info(f"payment_callback: received payment_method={payment_method}, body: {body}")
    try:
        payment_service_cls = PAYMENT_SYSTEM_SERVICES_MAP.get(int(payment_method))
    except Exception as e:
        logger.error(f"payment_callback: invalid payment_method={payment_method} error={e}")
        raise HTTPException(
            status_code=400,
            detail=f"Technical Error: {e}"
        )
    if not payment_service_cls:
        logger.error(f"payment_callback: payment system not ready payment_method={payment_method}")
        raise HTTPException(
            status_code=400,
            detail="This payment system is not ready"
        )

    # Чтение тела запроса
    payload = body.decode()
    payment_service = payment_service_cls()
    data = payment_service.prepare_payload(payload)
    logger.info(f"payment_callback: payload parsed operation_id={data.get('operation_id')} data={data}")
    operation = await operations_service.get_operation(data["operation_id"])
    if not operation:
        logger.error(f"payment_callback: operation not found operation_id={data.get('operation_id')}")
        raise HTTPException(
            status_code=400,
            detail="Wrong operation"
        )
    if data.get("status") in [OrderStatusChoices.REFUNED, OrderStatusChoices.PARTIALLY_REFUNDED]:
        await operations_service.update_order_refund(operation.id, data["addtional_fields"]["transaction_id"], status="done", updated_dt=datetime.now())
    logger.info(f"payment_callback: operation found operation_id={operation.id} status={operation.status}")
    application = await operations_service.get_application(operation.application_id)
    ofd_interface_parametrs = await operations_service.get_ofd_interface_parametres(operation.application_id)
    if application.is_fiscalisation and data.get("status") == OrderStatusChoices.PAID:
        logger.info(
            f"payment_callback: sending fiscal check operation_id={operation.id} ofd_interface={application.ofd_interface}")
        ofd_service = OFD_INTERFACE_SERVICE_MAP.get(application.ofd_interface)
        background_tasks.add_task(
            ofd_service().register_document,
            application,
            operation,
            ofd_interface_parametrs,
            operations_service,
            operation.nomenclature,
            "sell",
            order_id=operation.id,
            additional_data=operation.additional_data,
        )
        logger.info(f"payment_callback: fiscal check sent operation_id={operation.id}")
    if application.is_fiscalisation and data.get("status") in [
        OrderStatusChoices.PARTIALLY_REFUNDED, OrderStatusChoices.REFUNED
    ]:
        ofd_service = OFD_INTERFACE_SERVICE_MAP.get(application.ofd_interface)
        refund = await operations_service.get_order_refund(
            order_id=operation.id,
            transaction_id=data["addtional_fields"]["transaction_id"]
        )
        background_tasks.add_task(
            ofd_service().register_document,
            application,
            operation,
            ofd_interface_parametrs,
            operations_service,
            refund.nomenclature,
            "sell_refund",
            refund_id=refund.id
        )
    payment_system_parametres = await operations_service.get_payment_system_parametres(operation.application_id)
    payment_service.set_system_parameters(**payment_system_parametres)
    error = payment_service.check_payment(operation, data)
    if error:
        logger.warning(f"payment_callback: check_payment error={error} operation_id={operation.id}")
        raise HTTPException(
            status_code=400,
            detail=error
        )
    update_fields = [
        "payment_dt", "status", "fee", "invoice_id",
        "receipt_link", "crc",
    ]
    update_data = {field_name: data.get(field_name) for field_name in update_fields}
    logger.info(f"payment_callback: updating order operation_id={operation.id} update_data={update_data}")
    await operations_service.update_order(data['operation_id'], **update_data)

    status = OrderStatusChoices(operation.status)
    # Подготовка callback
    callback_payload = {
        "operation_id": operation.id,
        "invoice_id": operation.invoice_id,
        "final_price": float(operation.final_price),
        "discount_amount": float(operation.discount_amount),
        "user_id": operation.user_id,
        "receipt_link": operation.receipt_link,
        "fee": operation.fee,
        "currency": operation.currency,
        "status": status.value,
        "status_label": status.label
    }
    application = await operations_service.get_application(operation.application_id)
    if application.callback_url:
        logger.info(
            f"payment_callback: sending outgoing callback to {application.callback_url} operation_id={operation.id}")
        background_tasks.add_task(perform_callback, application.callback_url, callback_payload)
    return {"detail": "OK"}


@router.post("/callback-atol/")
async def callback_atol(request: Request, operations_service=Depends(OperationsService)):
    logger.info("callback_atol: received callback from ATOL")
    try:
        payload = await request.json()
        logger.info(f"callback_atol: payload={payload}")
        atol_service = AtolService()
        await atol_service.check_callback_data(payload, operations_service)
        logger.info(
            f"callback_atol: processed successfully external_id={payload.get('external_id')} status={payload.get('status')}")
    except Exception as exc:
        logger.error(f"callback_atol: processing error type={type(exc).__name__} error={exc}")
        raise HTTPException(status_code=400, detail="Invalid data")
