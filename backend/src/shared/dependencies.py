"""FastAPI dependency factories shared across all feature routers.

Provides reusable ``Depends(...)`` callables for:

- **Authentication** — ``get_current_user`` validates the JWT bearer token
  and returns the decoded claims.
- **Authorisation** — ``require_role`` is a factory that produces a
  dependency which asserts that the current user holds one of the
  allowed roles.
- **Pagination** — ``get_pagination`` captures page / sort query
  parameters into a ``PaginationParams`` object.

Typical usage::

    from src.shared.dependencies import get_current_user, require_role

    @router.get("/admin/users")
    async def list_users(
        user: dict = Depends(require_role("admin")),
    ) -> list[UserOut]:
        ...
"""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer

from src.shared.exceptions import AuthenticationError, AuthorizationError
from src.shared.pagination import PaginationParams
from src.shared.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate the bearer token and return the decoded JWT claims.

    This is the **primary authentication dependency**.  Every
    protected endpoint should depend on this (directly or via
    ``require_role``).

    Args:
        token: The raw JWT extracted from the ``Authorization`` header
            by ``OAuth2PasswordBearer``.

    Returns:
        A dictionary with at least ``"sub"`` (user id) and
        ``"role"`` claims.

    Raises:
        AuthenticationError: If the token is missing, expired, or
            otherwise invalid.
    """
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise AuthenticationError("Expected an access token, got a different token type")

    return payload


# ------------------------------------------------------------------
# Authorisation
# ------------------------------------------------------------------

def require_role(*allowed_roles: str) -> Callable:
    """Factory that returns a dependency enforcing role-based access.

    Args:
        *allowed_roles: One or more role strings (e.g. ``"admin"``,
            ``"user"``).  The user must hold at least one.

    Returns:
        A FastAPI-compatible async dependency function.

    Example::

        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: UUID,
            current_user: dict = Depends(require_role("admin")),
        ) -> ApiResponse:
            ...
    """

    async def _role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "")
        if user_role not in allowed_roles:
            raise AuthorizationError(
                f"Role '{user_role}' is not authorised. "
                f"Required: {', '.join(allowed_roles)}"
            )
        return current_user

    return _role_checker


# ------------------------------------------------------------------
# Pagination
# ------------------------------------------------------------------

async def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(default=50, ge=1, le=100, description="Items per page"),
    sort_by: str | None = Query(default=None, description="Column to sort by"),
    sort_order: str = Query(default="desc", description="Sort direction: asc or desc"),
) -> PaginationParams:
    """Build a ``PaginationParams`` from query-string values.

    Use as ``pagination = Depends(get_pagination)`` in any list
    endpoint.

    Returns:
        A validated ``PaginationParams`` instance.
    """
    return PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )
