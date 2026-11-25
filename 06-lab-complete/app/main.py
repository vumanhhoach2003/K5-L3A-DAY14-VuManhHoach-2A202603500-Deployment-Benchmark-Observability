"""
Production AI Agent — Part 6 Final Project
"""
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, record_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask


# Tiêu chí 10: Structured logging — mỗi dòng log của app là 1 JSON object hợp lệ
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "lvl": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(log_obj, ensure_ascii=False)


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.propagate = False
_handler = logging.StreamHandler()
_handler.setFormatter(JsonFormatter())
logger.handlers.clear()
logger.addHandler(_handler)


# Tiêu chí 11: Graceful shutdown với FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(json.dumps({"event": "startup", "status": "running", "env": settings.environment}))
    yield
    logger.info(json.dumps({"event": "shutdown", "status": "gracefully_stopped"}))


app = FastAPI(title="Production AI Agent", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "lvl": "INFO",
        "event": "request",
        "path": request.url.path,
        "method": request.method,
        "status": response.status_code,
        "ms": duration_ms,
    }))
    return response


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = "default"


# Tiêu chí 4: Liveness endpoint (luôn 200 khi process còn chạy)
@app.get("/health")
def health():
    return {"status": "ok"}


# Tiêu chí 5: Readiness endpoint (200 khi sẵn sàng, 503 khi Redis mất kết nối)
@app.get("/ready")
def ready():
    if not redis_healthy():
        raise HTTPException(status_code=503, detail="Redis connection failed")
    return {"status": "ready"}


# Endpoint chính: /ask
@app.post("/ask")
def ask(body: AskRequest, api_key: str = Depends(verify_api_key)):
    # Tiêu chí 7: Rate limiting
    check_rate_limit(api_key)

    # Tiêu chí 8: Cost guard trước khi gọi LLM
    check_budget()

    # Gọi LLM (mock)
    answer = llm_ask(body.question)

    # Ghi nhận chi phí sau khi hoàn thành
    input_tokens = len(body.question.split()) * 2 + 10
    output_tokens = len(answer.split()) * 2 + 10
    record_cost(input_tokens, output_tokens)

    return {"question": body.question, "answer": answer}
