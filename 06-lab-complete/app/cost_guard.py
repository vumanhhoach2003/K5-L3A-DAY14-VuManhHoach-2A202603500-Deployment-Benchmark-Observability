"""
Cost guard (tiêu chí 8).
"""
from fastapi import HTTPException
from app.config import settings
from app.redis_client import get_redis

PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

_fallback_cost = 0.0


def get_current_cost() -> float:
    client = get_redis()
    if client:
        try:
            val = client.get("total_cost_usd")
            return float(val) if val else 0.0
        except Exception:
            pass
    return _fallback_cost


def check_budget() -> None:
    """Gọi TRƯỚC khi gọi LLM. Hết budget → raise HTTPException(status_code=402)."""
    current_cost = get_current_cost()
    budget_limit = min(settings.daily_budget_usd, settings.monthly_budget_usd)
    if current_cost >= budget_limit:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Payment Required",
                "message": "Budget exceeded",
                "used_usd": current_cost,
                "budget_usd": budget_limit,
            },
        )


def record_cost(input_tokens: int, output_tokens: int) -> float:
    """Gọi SAU khi gọi LLM. Cộng chi phí của request vào tổng, trả về chi phí request."""
    cost = (input_tokens / 1000.0) * PRICE_INPUT_PER_1K + (output_tokens / 1000.0) * PRICE_OUTPUT_PER_1K
    global _fallback_cost
    _fallback_cost += cost
    client = get_redis()
    if client:
        try:
            client.incrbyfloat("total_cost_usd", cost)
        except Exception:
            pass
    return cost
