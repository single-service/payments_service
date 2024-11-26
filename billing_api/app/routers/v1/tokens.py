from datetime import datetime, timedelta
import uuid

from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
import jwt

from app.services.tokens import TokensService
from app.schemas.tokens import TokenCreateRequest, TokenCheckRequest
from app.utils.auth import JWTAuth


router = APIRouter()


def generate_token() -> str:
    return uuid.uuid4().hex


@router.post("/create-token")
async def create_token(
    request: TokenCreateRequest,
    user_id: bool = Depends(JWTAuth),
    token_service: TokensService = Depends(),
):
    token_type = request.token_type
    if token_type < 1 or token_type > 4:
        raise HTTPException(status_code=400, detail="Token type must be from 1 to 4")
    # Генерируем токен и устанавливаем время истечения (например, 30 минут)
    token_value = generate_token()
    expire_at = datetime.now() + timedelta(days=360)
    token_instance = await token_service.get_user_token(user_id)
    if not token_instance:
        status = await token_service.create_token(
            user_id=user_id,
            token=token_value,
            expire_at=expire_at,
            token_type=request.token_type
        )
    else:
        # update token
        status = await token_service.update_token(
            user_id=user_id,
            token=token_value,
            expire_at=expire_at,
            token_type=request.token_type
        )
    if not status:
        raise HTTPException(status_code=400, detail="Error occur")
    return {
        "msg": "Token created successfully",
        "token": token_value,
        "expire_at": expire_at
    }



@router.post("/check-token")
async def check_token(
    request: TokenCheckRequest,
    user_id: bool = Depends(JWTAuth),
    token_service: TokensService = Depends(),
):
    token = request.token
    token_instance = await token_service.get_user_token(user_id)
    if not token_instance:
        raise HTTPException(status_code=400, detail="Token not found")
    print("Token eq", token, token_instance.token)
    if token != token_instance.token:
        raise HTTPException(status_code=400, detail="Wrong token")
    return {
        "token": token_instance.token,
        "expire_at": token_instance.expire_at,
        "token_type": token_instance.token_type
    }