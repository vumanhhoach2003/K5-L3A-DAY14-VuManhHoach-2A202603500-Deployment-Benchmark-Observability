"""
Kết nối Redis dùng chung cho rate limiter và cost guard.
"""
import redis
from app.config import settings


def get_redis():
    """Tạo client Redis với timeout ngắn, không raise exception nếu lỗi."""
    if not settings.redis_url:
        return None
    try:
        client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        return client
    except Exception:
        return None


def redis_healthy() -> bool:
    """Kiểm tra Redis sẵn sàng hay không cho /ready probe."""
    try:
        client = get_redis()
        if client is None:
            return False
        return bool(client.ping())
    except Exception:
        return False
