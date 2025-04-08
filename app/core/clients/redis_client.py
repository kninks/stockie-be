# app/core/clients/redis_client.py
import redis.asyncio as redis

from app.core.settings.config import config

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)
