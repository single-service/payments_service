import logging
from typing import Optional, Dict, List
import json
from json import JSONDecodeError
from uuid import UUID
from datetime import datetime

from fastapi import Depends
from aioredis import Redis

from .redis_connector import get_redis
from app.settings import settings
from app.schemas.models import AiUserModelResponse


logger = logging.getLogger("info")


class JSONModelEncoder(json.JSONEncoder):
    """JSON кодировщик, который корректно обрабатывает UUID и datetime поля"""

    def default(self, obj):
        # Если UUID, возвращаем строку
        if isinstance(obj, UUID):
            return obj.hex
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Cacher:
    """Класс для кэширования в Redis"""

    # Префикс ключей кэша
    cache_prefix = settings.CACHE_PREFIX

    # Баланс пользователя
    balance_prefix = f'{cache_prefix}:balance'                          # Префикс для ключей
    balance_expiration = 60 * 60                                        # Длительность хранения (час)

    # Модели пользователя
    models_prefix = f'{cache_prefix}:models'                            # Префикс для ключей
    models_expiration = 60 * 60 * 24                                    # Длительность хранения (сутки)

    # Счётчик запросов к API
    counter_prefix = f'{cache_prefix}:user_api_count'                   # Префикс для ключей

    def __init__(self, client: Redis = Depends(get_redis)):
        self.client = client

    async def get_user_balance(self, user_id: str) -> Optional[int]:
        """Возвращает баланс переданного пользователя, если он есть в кэше"""

        key = f'{self.balance_prefix}:{user_id}'
        balance = await self.client.get(key)

        if balance and balance.decode().isnumeric():
            return int(balance.decode())

        return None

    async def set_user_balance(self, user_id: str, balance: int, expiration_time: Optional[int] = None):
        """Кэширует баланс переданного пользователя"""
        key = f'{self.balance_prefix}:{user_id}'
        ex = expiration_time or self.balance_expiration
        await self.client.set(key, balance, ex=ex)

    async def get_user_models(self, user_id: str) -> Optional[List[Dict]]:
        """Возвращает модели пользователя с их версиями"""
        key = f'{self.models_prefix}:{user_id}'

        value = await self.client.get(key)
        if not value:
            return None

        try:
            models = json.loads(value)
        except JSONDecodeError:
            logger.error(f'Invalid JSON value is stored by key {key}: {value}')
            return None

        return models

    async def set_user_models(
        self,
        user_id: str,
        models: List[AiUserModelResponse],
        expiration_time: Optional[int] = None,
    ):
        """Кэширует модели пользователя с их версиями. Хранит их в кэше json-строкой."""

        key = f'{self.models_prefix}:{user_id}'
        expiration_time = expiration_time or self.models_expiration

        # Конвертация в JSON
        models = [model.dict() for model in models]
        value = json.dumps(models, cls=JSONModelEncoder)

        await self.client.set(key, value=value, ex=expiration_time)

    async def incr_counter(self, user_id: str) -> int:
        """Увеличивает счётчик запросов на 1"""
        key = f'{self.counter_prefix}:{user_id}'
        return await self.client.incr(key, amount=1)

    async def decr_counter(self, user_id: str, amount: int) -> int:
        """Уменьшает счётчик на указанное значение"""
        key = f'{self.counter_prefix}:{user_id}'
        return await self.client.decr(key, amount)
