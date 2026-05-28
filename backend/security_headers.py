"""HTTP hardening middleware for the public web app."""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque
from urllib.parse import urlparse

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

DEFAULT_ALLOWED_ORIGINS = {
    "https://detective-hermes-agent.vercel.app",
    "http://127.0.0.1:8011",
    "http://localhost:8011",
}


def allowed_origins() -> set[str]:
    configured = os.getenv("ALLOWED_ORIGINS", "")
    values = {item.strip().rstrip("/") for item in configured.split(",") if item.strip()}
    return values or DEFAULT_ALLOWED_ORIGINS


class SecurityMiddleware(BaseHTTPMiddleware):
    """Adds request guards and response headers aligned with OWASP basics."""

    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, Deque[float]] = defaultdict(deque)
        self.max_body_bytes = int(os.getenv("MAX_REQUEST_BODY_BYTES", str(8 * 1024 * 1024)))

    async def dispatch(self, request: Request, call_next):
        blocked = self._enforce_content_length(request) or self._enforce_origin(request) or self._enforce_rate_limit(request)
        if blocked:
            self._apply_headers(blocked)
            return blocked
        response = await call_next(request)
        self._apply_headers(response)
        return response

    def _client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        ip = forwarded_for.split(",")[0].strip() or (request.client.host if request.client else "unknown")
        return f"{ip}:{request.url.path}"

    def _rate_limit(self, path: str) -> tuple[int, int]:
        if path.startswith("/auth/"):
            return int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "12")), 60
        if path == "/investigate":
            return int(os.getenv("INVESTIGATION_RATE_LIMIT_PER_MINUTE", "20")), 60
        return int(os.getenv("APP_RATE_LIMIT_PER_MINUTE", "180")), 60

    def _enforce_rate_limit(self, request: Request) -> Response | None:
        limit, window = self._rate_limit(request.url.path)
        now = time.time()
        key = self._client_key(request)
        bucket = self._buckets[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            return JSONResponse({"detail": "Too many requests. Please slow down."}, status_code=429)
        bucket.append(now)
        return None

    def _enforce_content_length(self, request: Request) -> Response | None:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_bytes:
            return JSONResponse({"detail": "Request body too large"}, status_code=413)
        return None

    def _enforce_origin(self, request: Request) -> Response | None:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        origin = request.headers.get("origin")
        if not origin:
            return None
        host_origin = f"{request.url.scheme}://{request.headers.get('host', '')}".rstrip("/")
        if origin.rstrip("/") == host_origin:
            return None
        if origin.rstrip("/") not in allowed_origins():
            return JSONResponse({"detail": "Cross-origin request blocked"}, status_code=403)
        return None

    def _apply_headers(self, response: Response) -> None:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https://media.pollinations.ai; "
            "connect-src 'self' https://gen.pollinations.ai https://media.pollinations.ai https://opencode.ai; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; "
            "upgrade-insecure-requests"
        )
