"""Shared infrastructure layer for EchoSmart.

This package provides cross-cutting concerns that **every** feature
module may depend on but that contain **no** feature-specific logic:

- ``exceptions`` — domain exception hierarchy
- ``responses``  — standard API response envelopes
- ``pagination`` — generic pagination primitives
- ``security``   — password hashing and JWT management
- ``repository`` — generic CRUD repository pattern
- ``dependencies`` — reusable FastAPI dependency factories

Public re-exports below keep imports short::

    from src.shared import NotFoundError, ApiResponse, BaseRepository
"""

from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from src.shared.pagination import PaginatedResponse, PaginationParams
from src.shared.repository import BaseRepository
from src.shared.responses import ApiResponse, ErrorResponse
from src.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    # Exceptions
    "EchoSmartError",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "RateLimitError",
    # Responses
    "ApiResponse",
    "ErrorResponse",
    # Pagination
    "PaginationParams",
    "PaginatedResponse",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    # Repository
    "BaseRepository",
]
