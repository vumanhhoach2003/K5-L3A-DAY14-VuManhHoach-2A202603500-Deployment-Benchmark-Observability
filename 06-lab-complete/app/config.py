"""
Config — 12-Factor: mọi cấu hình đọc từ biến môi trường.
"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    agent_api_key: str = os.getenv("AGENT_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    daily_budget_usd: float = float(os.getenv("DAILY_BUDGET_USD", "1.0"))
    monthly_budget_usd: float = float(os.getenv("MONTHLY_BUDGET_USD", "10.0"))


settings = Settings()
