import jwt
import hashlib

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.settings import settings
from app.database_connector import get_db
from app.models import ApplicationToken

# Настройка Bearer авторизации
security = HTTPBearer()

# Функция для проверки токена
def JWTAuth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    SCHEME_BEARER = "Bearer"
    scheme = credentials.scheme
    if scheme != SCHEME_BEARER:
        raise HTTPException(status_code=401, detail="Invalid token")

    token = credentials.credentials.replace(f"{SCHEME_BEARER} ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def TokenAuth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # Проверяем, что схема токена равна "Token"
    SCHEME_TOKEN = "Token"
    token_credentials = credentials.credentials.split(" ")
    scheme = token_credentials[0]
    if scheme != SCHEME_TOKEN or len(token_credentials) != 2:
        raise HTTPException(status_code=401, detail="Invalid token scheme")

    # Получаем полный токен и хэшируем его
    full_token = credentials.credentials.replace(f"{SCHEME_TOKEN} ", "")
    hashed_token = hashlib.sha512(full_token.encode()).hexdigest()

    # Ищем хэш токена в базе данных
    application_token = db.query(ApplicationToken).filter_by(token=hashed_token).first()
    if not application_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Возвращаем id токена или связанного пользователя
    return application_token.application_id
