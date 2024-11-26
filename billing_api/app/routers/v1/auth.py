from fastapi import FastAPI, APIRouter, HTTPException, Depends

from app.services.users import UserService
from app.schemas.auth import SignupRequest, SigninRequest, RefreshRequest


router = APIRouter()

# Эндпоинт регистрации
@router.post("/signup")
async def signup(
    request: SignupRequest,
    user_service: UserService = Depends(),
): 
    # Теперь у тебя есть доступ к данным тела запроса через переменную `request`
    username = request.username
    email = request.email
    password = request.password
    first_name = request.first_name
    last_name = request.last_name
    phone = request.phone  # Можно использовать phone, если оно указано
    # Проверка на существование пользователя с таким username или email
    db_user = await user_service.check_user_exist(email)
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    # Создаем нового пользователя
    status = await user_service.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        username=username
    )
    if not status:
        raise HTTPException(status_code=400, detail="Error creating user")
    return {"msg": "User created successfully"}


# Эндпоинт авторизации
@router.post("/signin")
async def signin(
    request: SigninRequest,
    user_service: UserService = Depends(),
):
    email = request.email
    password = request.password
    user = await user_service.check_login(
        email=email,
        password=password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Wrong email or password")

    # Данные для токенов
    token_data = {"sub": user.email, "user_id": user.id}

    # Создание токенов
    access_token = user_service.create_access_token(data=token_data)
    refresh_token = user_service.create_refresh_token(data=token_data)
    await user_service.update_last_login(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Эндпоинт refresh
@router.post("/refresh")
async def signin(
    request: RefreshRequest,
    user_service: UserService = Depends(),
):
    try:
        token_data = user_service.parse_token(request.refresh)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Bad token") 
    del token_data["exp"]
    access_token = user_service.create_access_token(data=token_data)
    refresh_token = user_service.create_refresh_token(data=token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
