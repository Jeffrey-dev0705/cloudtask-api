import time

from fastapi import HTTPException, Request
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

settings = get_settings()
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

