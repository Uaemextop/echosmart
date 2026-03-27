"""Middleware de autenticación — Validación JWT."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware para validar JWT en cada request."""

    async def dispatch(self, request: Request, call_next):
        # TODO: Validar token JWT del header Authorization
        response = await call_next(request)
        return response
