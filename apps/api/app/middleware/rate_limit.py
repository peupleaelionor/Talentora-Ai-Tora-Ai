from __future__ import annotations

import time
from collections import defaultdict
from typing import DefaultDict, Deque
from collections import deque

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)

# Configurable limits — move to settings if you need per-tier overrides
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 120  # requests per window per IP

# In-memory sliding window store: ip -> deque of timestamps
_store: DefaultDict[str, Deque[float]] = defaultdict(deque)


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window in-process rate limiter.

    For production deployments, replace _store with a Redis-backed
    implementation (e.g. redis-py INCR + EXPIRE) for multi-process safety.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ip = _get_client_ip(request)
        now = time.monotonic()
        window_start = now - _WINDOW_SECONDS

        bucket = _store[ip]
        # Evict timestamps outside the current window
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        remaining = max(0, _MAX_REQUESTS - len(bucket))
        reset_ts = int(time.time()) + _WINDOW_SECONDS

        if len(bucket) >= _MAX_REQUESTS:
            logger.warning("Rate limit exceeded", ip=ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={
                    "X-RateLimit-Limit": str(_MAX_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_ts),
                    "Retry-After": str(_WINDOW_SECONDS),
                },
            )

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        response.headers["X-RateLimit-Reset"] = str(reset_ts)
        return response
