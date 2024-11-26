import aioredis

from app.settings import settings


redis = aioredis.from_url(settings.REDIS_CONNECTION_URL)


async def get_redis():
    redis_client = redis.client()
    try:
        yield redis_client
    finally:
        await redis_client.close()
