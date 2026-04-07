import aiohttp

from app import redis_manager
from app.settings.common import CommonConfig
from app.logger import get_logger

logger = get_logger()


class Atol:

    # BASE_URL = "https://online.atol.ru/possystem/v4"
    # BASE_URL = "https://testonline.atol.ru/possystem/v4"

    def __init__(self, login, password, group_code):
        self.login = login
        self.password = password
        self.group_code = group_code

    async def auth(self):
        redis_key = f"{self.login}_atol_token"

        token = await redis_manager.get(redis_key)
        if token:
            return token.decode("utf-8")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{CommonConfig.ATOL_BASE_URL}/getToken",
                    headers={
                        "Content-Type": "application/json; charset=utf-8"
                    },
                    json={
                        "login": self.login,
                        "pass": self.password
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    body = await response.json()
            token = body.get("token")
            if token:
                await redis_manager.set(redis_key, token, expire=86400)
                return token
            error = body.get("error")
            logger.error(f"atol Ошибка при авторизации пользователя в АТОЛ: {error}")
            raise Exception(f"Ошибка при авторизации пользователя в АТОЛ: {error}")
        except aiohttp.ClientError as exc:
            logger.error(f"atol Ошибка соединения с АТОЛ: {exc}")
            raise Exception(
                f"Ошибка соединения с АТОЛ: {exc}"
            ) from exc

    async def register_document(self, data: dict, operation_type: str):
        token = await self.auth()
        logger.info(f"atol data: {data}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{CommonConfig.ATOL_BASE_URL}/{self.group_code}/{operation_type}",
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Token": token
                    },
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    logger.info(f"atol status {response.status}, response: {response.content}")
                    body = await response.json()
            uuid = body.get("uuid")
            status = body.get("status")
            error = body.get("error")
            return uuid, status, error
        except aiohttp.ClientError as exc:
            logger.error(f"atol Ошибка соединения с АТОЛ: {exc}")
            raise Exception(
                f"atol Ошибка соединения с АТОЛ: {exc}"
            ) from exc
