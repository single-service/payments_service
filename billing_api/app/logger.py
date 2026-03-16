import logging
import os
from logging.config import dictConfig

UDP_HOST = os.getenv("UDP_LOG_HOST", "5.35.31.101")
UDP_PORT = int(os.getenv("UDP_LOG_PORT", "9999"))
SERVER_NAME = os.getenv("SERVER_NAME", "payment-service")
IS_LOGGER = os.getenv("IS_LOGGER", "").lower() == "true"

_UDP_HANDLERS = ["udp", "console"] if IS_LOGGER else ["console"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "logger": {
            "handlers": _UDP_HANDLERS,
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": _UDP_HANDLERS,
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": _UDP_HANDLERS,
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": _UDP_HANDLERS,
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": _UDP_HANDLERS,
            "level": "INFO",
            "propagate": False,
        },
    },
}

if IS_LOGGER:
    LOGGING["handlers"]["udp"] = {
        "level": "INFO",
        "class": "udp_logger.logger.udp_handler.UDPSyncLoggerHandler",
        "udp_host": UDP_HOST,
        "udp_port": UDP_PORT,
        "server_name": SERVER_NAME,
    }


def setup_logging():
    dictConfig(LOGGING)


def get_logger(name: str = "logger") -> logging.Logger:
    return logging.getLogger(name)
