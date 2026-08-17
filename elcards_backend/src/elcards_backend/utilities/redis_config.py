from upstash_redis.asyncio import Redis
from elcards_backend.settings import settings

redis = Redis(url=settings.redis_url, token=settings.redis_token)

async def set_redis(key: int | str, seconds: int, value: int | str | bool) -> bool:    
    await redis.setex(key, seconds, value)
    stored_value = await redis.get(key)
    if stored_value and stored_value == value:
        return True
    return False
