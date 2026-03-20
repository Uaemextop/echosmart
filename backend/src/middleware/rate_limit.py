"""Middleware de rate limiting."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar requests por IP/usuario."""

    async def dispatch(self, request: Request, call_next):
        # TODO: Implementar rate limiting con Redis
        response = await call_next(request)
        return response
