from fastapi import APIRouter

# from app.routers.v1 import balance, models, predict, connection
from app.routers.v1 import connection


router = APIRouter(prefix='/api/v1')

router.include_router(connection.router, tags=['Connection'])
# router.include_router(auth.router, tags=['Auth'])
# router.include_router(tokens.router, tags=['Tokens'])
# router.include_router(users.router, tags=['User'])
