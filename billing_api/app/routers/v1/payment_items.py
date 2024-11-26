from typing import List

from fastapi import APIRouter, Depends, Query

from app.schemas.payment_items import PaymentItemGroupSchema, PaymentItemSchema
from app.utils.auth import TokenAuth
from app.services.payment_items_service import PaymentItemsService


router = APIRouter()


@router.get(
    '/groups/',
    response_model=List[PaymentItemGroupSchema],
    include_in_schema=True,
)
async def get_groups(
    application_id=Depends(TokenAuth),
    payment_items_service = Depends(PaymentItemsService)
):
    """Список групп"""
    groups = await payment_items_service.get_groups(application_id)
    return groups


@router.get(
    '/payment-items/',
    response_model=List[PaymentItemSchema],
    include_in_schema=True,
)
async def get_payment_items(
    application_id=Depends(TokenAuth),
    payment_items_service = Depends(PaymentItemsService),
    group_id: str = Query(None, description="Optional status filter")
):
    """Список позиций"""
    items = await payment_items_service.get_payment_items(application_id, group_id=group_id)
    print(items)
    return items
