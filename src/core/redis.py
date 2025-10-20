from redis.asyncio import Redis
from core.config import redis_settings


async def setup_redis() -> Redis:
    redis = Redis.from_url(redis_settings.REDIS_URL, decode_response=True)
    await redis.ping()
    return redis
