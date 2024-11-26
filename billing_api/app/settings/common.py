import logging
import os
import re


class CommonConfig:
    # App
    API_HOST = os.getenv("HOST", "0.0.0.0")  # noqa: S104
    API_PORT = 8000
    RELOAD = True
    DEBUG: bool = os.getenv("DEBUG", False) in ["1", "True", "true", "y", True, 1]
    SHOW_DOCS: bool = True
    MEDIA_DIR = "media"
    API_ROOT: str = os.getenv("API_ROOT", "/v1")

    # Celery
    BROKER_URL = os.getenv("BROKER_URL")

    # Authorization
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECRET_APP_KEY = os.getenv("SECRET_APP_KEY")
    JWT_ALGORITHM = "HS256"

    # Database
    DB_HOST = os.getenv("DB_URL")
    DB_PORT =os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DB_URL: str = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URL_ASYNC: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    DB_POOL_MINSIZE: int = 5
    DB_POOL_SIZE: int = 20

    # Cache
    REDIS_CONNECTION_URL = os.getenv("REDIS_URL")
    CACHE_PREFIX = "prediction_service"

    # HTTP
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    RETRY_MAX_TIME: int = int(os.getenv("RETRY_MAX_TIME", 300))
    HTTP_CLIENT_TIMEOUT_REQUEST = os.environ.get("HTTP_CLIENT_TIMEOUT_REQUEST", 5)
    HTTP_CLIENT_MAX_FAILED_SESSIONS = os.environ.get("HTTP_CLIENT_MAX_FAILED_SESSIONST", 10)

    # Yandex Storage
    YS_ACCESS_KEY_ID = os.getenv("YS_ACCESS_KEY_ID")
    YS_SECRET_ACCESS_KEY = os.getenv("YS_SECRET_ACCESS_KEY")
    YS_DATASETS_BUCKET_NAME = os.getenv("YS_DATASETS_BUCKET_NAME", "dev-cold")
    YS_MODELS_BUCKET_NAME = os.getenv("YS_MODELS_BUCKET_NAME", "dev-standart")

    YS_DATASET_DIR = os.getenv("YS_DATASET_DIR", "uploaded_datasets")
    YS_MODELS_DIR = os.getenv("YS_MODELS_DIR", "models")
    YS_PRESIGNED_LINK_EXPIRATION = os.getenv("YS_PRESIGNED_LINK_EXPIRATION", 3600)

    # Logging
    DIR_LOGS = "/app/shared/logs"
    LOG_LEVEL_APP_ROUTERS_USER = os.getenv("LOG_LEVEL_APP_ROUTERS_USER")
    LOG_LEVEL = logging.ERROR
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(funcName)s - %(message)s",
            },
            "extended": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(funcName)s - %(message)s %(request)s %(response)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "formatter": "extended",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "*": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "debug": {
                "handlers": ["console"],
                "level": "DEBUG" if os.getenv("ENV") != "prod" else "ERROR",
                "propagate": False,
            },
        },
    }
