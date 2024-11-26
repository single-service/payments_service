from fastapi import APIRouter

# from app.routers.v1 import balance, models, predict, connection
from app.routers.v1 import connection, payment_items, operations


router = APIRouter(prefix='/api/v1')

router.include_router(connection.router, tags=['Connection'])
router.include_router(payment_items.router, tags=['Payment Items'])
router.include_router(operations.router, tags=['Billing'])
# router.include_router(tokens.router, tags=['Tokens'])
# router.include_router(users.router, tags=['User'])
