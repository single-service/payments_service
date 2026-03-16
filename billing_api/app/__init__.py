from app.utils.redis_manager import RedisManager
from app.settings.common import CommonConfig

print(CommonConfig.REDIS_HOST, CommonConfig.REDIS_PORT)
redis_manager = RedisManager(
    host=CommonConfig.REDIS_HOST,
    port=CommonConfig.REDIS_PORT,
)
