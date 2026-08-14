import time

from fastapi import HTTPException, Request
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

settings = get_settings()
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

async def fixed_window_limit(request: Request, limit: int = 120, window_seconds: int = 60) -> None:
    client = request.client.host if request.client else "unknown"
    window = int(time.time() // window_seconds)
    key = f"rl:{client}:{window}"
    try:
        value = await redis_client.incr(key)
        if value == 1:
            await redis_client.expire(key, window_seconds + 2)
        if value > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except HTTPException:
        raise
    except RedisError:
        # Fail open if Redis is temporarily unavailable.
        return
