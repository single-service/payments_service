import asyncio
import logging.config

import json_logging
import pytz
from app.utils import transport_manager
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from .routers.v1 import base
from .settings import settings
from .settings.json import CustomJSONLog, CustomRequestJSONLog


json_logging.CREATE_CORRELATION_ID_IF_NOT_EXISTS = False
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("info")
json_logging.init_fastapi(enable_json=True, custom_formatter=CustomJSONLog)

app_settings = {
    "title": "Billing Manager",
    "docs_url": "/api/v1/docs/",  # for monolith
    "openapi_url": "/api/v1/docs/docs/openapi.json",
}

if not settings.SHOW_DOCS:
    app_settings = {
        "docs_url": None,
        "openapi_url": None,
        "redoc_url": None,
    }


app = FastAPI(**app_settings)
timezone = pytz.timezone("Europe/Moscow")
json_logging.init_request_instrument(app=app, custom_formatter=CustomRequestJSONLog)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()  # noqa

    await transport_manager.connection_test_getter.startup()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logger.error(str(exc))
    print(f"Validation error: {str(exc)}")  # noqa: T201
    raise HTTPException(status_code=500, detail="Server error")


root_router = APIRouter()

root_router.include_router(base.router)

app.include_router(root_router)


CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hub2.ai",
    ],
    # allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=["*"],
)
