import time
import logging

from functools import wraps
from fastapi import Request, HTTPException
from typing import Callable, Dict, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

EXCLUDE_PATHS = ["/actuator", "/docs", "/openapi.json"]


def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    logger.info(f"Headers: {request.headers}")
    logger.info(f"X-Forwarded-For: {x_forwarded_for}")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        # fallback
        client_ip = request.client.host
    return client_ip


rate_limit_storage: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))


def limits(calls: int, period_seconds: int):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            client_ip = get_client_ip(request)
            key = f"{client_ip}:{func.__name__}"

            call_count, last_reset = rate_limit_storage[key]
            current_time = time.time()

            # 시간 창이 지났으면 초기화
            if current_time - last_reset > period_seconds:
                call_count = 0
                last_reset = current_time

            if call_count >= calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {calls} calls per {period_seconds} seconds.",
                )

            rate_limit_storage[key] = (call_count + 1, last_reset)

            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator
