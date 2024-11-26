import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import settings

# Настройка Bearer авторизации
security = HTTPBearer()


SCHEME_BEARER = "Bearer"

# Функция для проверки токена
def JWTAuth(credentials: HTTPAuthorizationCredentials = Depends(security)):
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