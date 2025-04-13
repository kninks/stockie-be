import redis.asyncio as redis

from app.core.settings.config import get_config

redis_client = redis.Redis(
    host=get_config().REDIS_HOST,
    port=get_config().REDIS_PORT,
    db=get_config().REDIS_DB,
    decode_responses=True,
)
