from datetime import datetime, timedelta
import uuid

from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
import jwt

from app.services.users import UserService
from app.schemas.tokens import TokenCreateRequest, TokenCheckRequest
from app.utils.auth import JWTAuth


router = APIRouter()


@router.get("/me")
async def create_token(
    user_id: bool = Depends(JWTAuth),
    user_service: UserService = Depends(),
):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong user")
    data = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "last_visit_date": user.last_visit_date,
    }
    return data
