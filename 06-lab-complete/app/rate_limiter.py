"""
Rate limiting (tiêu chí 7) sử dụng Sliding Window trong Redis.
"""
import time
from fastapi import HTTPException
from app.config import settings
from app.redis_client import get_redis

# In-memory fallback if Redis is not configured
_local_requests: dict[str, list[float]] = {}


def check_rate_limit(key: str) -> None:
    limit = settings.rate_limit_per_minute
    window = 60
    now = time.time()
    client = get_redis()

    if client:
        redis_key = f"rate_limit:{key}"
        try:
            pipe = client.pipeline()
            pipe.zremrangebyscore(redis_key, 0, now - window)
            pipe.zcard(redis_key)
            results = pipe.execute()
            current_count = results[1]

            if current_count >= limit:
                oldest = client.zrange(redis_key, 0, 0, withscores=True)
                retry_after = int(oldest[0][1] + window - now) + 1 if oldest else window
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(max(1, retry_after))},
                )

            pipe = client.pipeline()
            pipe.zadd(redis_key, {str(now): now})
            pipe.expire(redis_key, window)
            pipe.execute()
            return
        except HTTPException:
            raise
        except Exception:
            pass

    # Fallback in-memory
    timestamps = _local_requests.setdefault(key, [])
    cutoff = now - window
    _local_requests[key] = [t for t in timestamps if t > cutoff]
    if len(_local_requests[key]) >= limit:
        oldest = _local_requests[key][0]
        retry_after = int(oldest + window - now) + 1
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(max(1, retry_after))},
        )
    _local_requests[key].append(now)
