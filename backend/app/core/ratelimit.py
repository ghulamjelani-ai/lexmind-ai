"""Lightweight fixed-window rate limiting for sensitive endpoints.

Backed by Redis so limits are shared across replicas. It **fails open**: if
Redis is unreachable or errors, the request is allowed through — rate limiting
must never take authentication down. Keyed on the client IP (read from
X-Forwarded-For behind Railway/Vercel proxies).
"""

from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import HTTPException, Request, status

from app.core.config import get_settings

try:  # redis is a hard dep of the app (Celery broker); guard import just in case.
    import redis as _redis_lib
except Exception:  # pragma: no cover
    _redis_lib = None  # type: ignore[assignment]

# Sentinel: None = not yet initialised, False = unavailable, else a client.
_client: object = None


def _redis():
    global _client
    if _client is None:
        if _redis_lib is None:
            _client = False
        else:
            try:
                client = _redis_lib.Redis.from_url(
                    get_settings().redis_url,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                )
                client.ping()  # connect once now; if it fails we cache the miss
                _client = client
            except Exception:
                # Cache the failure so we never retry (and never pay the connect
                # timeout) on every request when Redis is absent — e.g. in tests.
                _client = False
    return _client or None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(bucket: str, limit: int, window_seconds: int) -> Callable[[Request], None]:
    """Return a FastAPI dependency allowing at most `limit` requests per
    `window_seconds` per client IP for `bucket`. Fails open on any Redis error."""

    def dependency(request: Request) -> None:
        client = _redis()
        if client is None:
            return  # fail open — Redis unavailable
        ip = _client_ip(request)
        window = int(time.time()) // window_seconds
        key = f"rl:{bucket}:{ip}:{window}"
        try:
            count = client.incr(key)
            if count == 1:
                client.expire(key, window_seconds)
        except Exception:
            return  # fail open — never block auth on a Redis hiccup
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait a moment and try again.",
            )

    return dependency
