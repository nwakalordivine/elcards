from upstash_redis import Redis
from elcards_backend.settings import settings

redis = Redis(url=settings.redis_url, token=settings.redis_token)


