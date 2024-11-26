from fastapi import APIRouter

from app.schemas.connection import LiveResponseSchema


router = APIRouter()


@router.get('/live/', response_model=LiveResponseSchema, include_in_schema=True)
async def get_live():
    """Метод live"""
    return {"live": "ok"}
