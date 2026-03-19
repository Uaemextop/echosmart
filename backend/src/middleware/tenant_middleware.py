"""Middleware de tenant — Inyección de tenant_id."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware para inyectar tenant_id en cada request."""

    async def dispatch(self, request: Request, call_next):
        # TODO: Extraer tenant_id del token JWT y agregarlo al request state
        response = await call_next(request)
        return response
