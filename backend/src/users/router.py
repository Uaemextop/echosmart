"""FastAPI router for the ``/api/v1/users`` endpoints.

All endpoints require the ``admin`` role via
``Depends(require_role("admin"))``.

The router is intentionally **thin** — it:

1. Parses the HTTP request (path params, query params, body).
2. Delegates to :class:`~src.users.service.UserManagementService`.
3. Wraps the result in :class:`~src.shared.responses.ApiResponse`.

All domain exceptions are translated to HTTP status codes via a
``_handle_domain_errors`` context manager.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.shared.dependencies import get_current_user, get_pagination, require_role
from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    ValidationError,
)
from src.shared.pagination import PaginationParams
from src.shared.responses import ApiResponse
from src.users.schemas import (
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from src.users.service import UserManagementService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# ------------------------------------------------------------------
# Error translation
# ------------------------------------------------------------------

_STATUS_MAP: dict[type[EchoSmartError], int] = {
    ValidationError: 422,
    NotFoundError: 404,
    ConflictError: 409,
    AuthenticationError: 401,
    AuthorizationError: 403,
}


@contextmanager
def _handle_domain_errors() -> Generator[None, None, None]:
    """Translate domain exceptions into ``HTTPException``."""
    try:
        yield
    except EchoSmartError as exc:
        status = _STATUS_MAP.get(type(exc), 500)
        raise HTTPException(status_code=status, detail=exc.message) from exc


# ------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------

def _user_service(db: Session = Depends(get_db)) -> UserManagementService:
    """FastAPI dependency that creates a ``UserManagementService``."""
    return UserManagementService(db)


def _get_tenant_id(
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UUID:
    """Resolve the tenant_id for the authenticated admin user."""
    user_id = UUID(current_user["sub"])
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise AuthenticationError("User account no longer exists")
    return user.tenant_id


# ------------------------------------------------------------------
# User CRUD (admin only)
# ------------------------------------------------------------------

@router.get("/", response_model=ApiResponse)
async def list_users(
    tenant_id: UUID = Depends(_get_tenant_id),
    pagination: PaginationParams = Depends(get_pagination),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """List all users in the admin's tenant with pagination."""
    with _handle_domain_errors():
        result = service.list_users(tenant_id, pagination)
    return ApiResponse(
        status="ok",
        data={
            "items": [UserResponse.model_validate(u).model_dump(mode="json") for u in result.items],
            "total": result.total,
            "page": result.page,
            "per_page": result.per_page,
            "pages": result.pages,
        },
    )


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_user(
    body: UserCreate,
    tenant_id: UUID = Depends(_get_tenant_id),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """Create a new user in the admin's tenant."""
    with _handle_domain_errors():
        user = service.create_user(tenant_id, body.model_dump())
    return ApiResponse(
        status="ok",
        message="User created successfully",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """Retrieve a single user by their ID."""
    with _handle_domain_errors():
        user = service.get_user(user_id)
    return ApiResponse(
        status="ok",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """Update an existing user (partial update supported)."""
    update_data = body.model_dump(exclude_unset=True)
    with _handle_domain_errors():
        user = service.update_user(user_id, update_data)
    return ApiResponse(
        status="ok",
        message="User updated successfully",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: UUID,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """Deactivate a user account (soft delete)."""
    with _handle_domain_errors():
        service.deactivate_user(user_id)
    return ApiResponse(
        status="ok",
        message="User deactivated successfully",
    )


@router.put("/{user_id}/role", response_model=ApiResponse)
async def change_user_role(
    user_id: UUID,
    body: UserRoleUpdate,
    _tenant_id: UUID = Depends(_get_tenant_id),
    service: UserManagementService = Depends(_user_service),
) -> ApiResponse:
    """Change a user's role."""
    with _handle_domain_errors():
        user = service.change_role(user_id, body.role)
    return ApiResponse(
        status="ok",
        message="User role updated successfully",
        data=UserResponse.model_validate(user).model_dump(mode="json"),
    )
