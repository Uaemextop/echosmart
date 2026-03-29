"""FastAPI router for the ``/api/v1/auth`` endpoints.

The router is intentionally **thin** — it:

1. Parses the HTTP request into a Pydantic schema.
2. Delegates to :class:`~src.auth.service.AuthService`.
3. Wraps the result in :class:`~src.shared.responses.ApiResponse`.

All domain exceptions are caught and translated to appropriate
``HTTPException`` status codes via a local ``_handle_domain_errors``
context manager.  This keeps endpoints clean and consistent.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth.schemas import (
    AdminLoginRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserProfile,
)
from src.auth.service import AuthService
from src.database import get_db
from src.shared.dependencies import get_current_user
from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    ValidationError,
)
from src.shared.responses import ApiResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


# ------------------------------------------------------------------
# Error translation
# ------------------------------------------------------------------

_STATUS_MAP: dict[type[EchoSmartError], int] = {
    ValidationError: 422,
    AuthenticationError: 401,
    AuthorizationError: 403,
    NotFoundError: 404,
    ConflictError: 409,
}


@contextmanager
def _handle_domain_errors() -> Generator[None, None, None]:
    """Translate domain exceptions into ``HTTPException``.

    Usage::

        with _handle_domain_errors():
            result = service.do_something()
    """
    try:
        yield
    except EchoSmartError as exc:
        status = _STATUS_MAP.get(type(exc), 500)
        raise HTTPException(status_code=status, detail=exc.message) from exc


# ------------------------------------------------------------------
# Factory
# ------------------------------------------------------------------

def _auth_service(db: Session = Depends(get_db)) -> AuthService:
    """FastAPI dependency that creates an ``AuthService``."""
    return AuthService(db)


# ------------------------------------------------------------------
# Public endpoints (no authentication required)
# ------------------------------------------------------------------


@router.post("/register", response_model=ApiResponse, status_code=201)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Register a new user with a kit serial code.

    Validates the serial, creates user + default tenant, and marks the
    serial as registered.
    """
    with _handle_domain_errors():
        user = service.register(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            serial_code=body.serial_code,
            phone=body.phone,
        )
    return ApiResponse(
        status="ok",
        message="User registered successfully",
        data=UserProfile.model_validate(user).model_dump(mode="json"),
    )


@router.post("/login", response_model=ApiResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Authenticate with e-mail and password."""
    with _handle_domain_errors():
        tokens = service.login(email=body.email, password=body.password)
    return ApiResponse(
        status="ok",
        message="Login successful",
        data=TokenResponse(**tokens).model_dump(),
    )


@router.post("/admin/login", response_model=ApiResponse)
async def admin_login(
    body: AdminLoginRequest,
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Authenticate as an admin (requires admin role + optional 2FA)."""
    with _handle_domain_errors():
        tokens = service.admin_login(
            email=body.email,
            password=body.password,
            totp_code=body.totp_code,
        )
    return ApiResponse(
        status="ok",
        message="Admin login successful",
        data=TokenResponse(**tokens).model_dump(),
    )


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    body: RefreshRequest,
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Exchange a refresh token for a new access + refresh pair."""
    with _handle_domain_errors():
        tokens = service.refresh_token(body.refresh_token)
    return ApiResponse(
        status="ok",
        message="Token refreshed",
        data=TokenResponse(**tokens).model_dump(),
    )


@router.post("/logout", response_model=ApiResponse)
async def logout() -> ApiResponse:
    """Log out the current session.

    .. note::

        Full token blacklisting (e.g. via Redis) is not yet
        implemented.  The client should discard its tokens.
    """
    return ApiResponse(status="ok", message="Logged out successfully")


@router.post("/forgot-password", response_model=ApiResponse)
async def forgot_password(body: ForgotPasswordRequest) -> ApiResponse:
    """Request a password-reset e-mail.

    .. note::

        E-mail delivery is not yet wired.  The endpoint always returns
        a generic success message to avoid leaking whether the address
        is registered.
    """
    return ApiResponse(
        status="ok",
        message=(
            "If the email is registered, you will receive "
            "password reset instructions"
        ),
    )


@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(body: ResetPasswordRequest) -> ApiResponse:
    """Confirm a password reset using the token from the e-mail.

    .. note::

        Not yet implemented — placeholder for the reset flow.
    """
    return ApiResponse(
        status="ok",
        message="Password has been reset successfully",
    )


# ------------------------------------------------------------------
# Protected endpoints (require authentication)
# ------------------------------------------------------------------


@router.get("/me", response_model=ApiResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Return the authenticated user's profile."""
    user_id = UUID(current_user["sub"])
    with _handle_domain_errors():
        user = service.get_profile(user_id)
    return ApiResponse(
        status="ok",
        data=UserProfile.model_validate(user).model_dump(mode="json"),
    )


@router.put("/me", response_model=ApiResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Update the authenticated user's profile (name, phone)."""
    user_id = UUID(current_user["sub"])
    update_data = body.model_dump(exclude_unset=True)

    with _handle_domain_errors():
        user = service.update_profile(user_id, update_data)
    return ApiResponse(
        status="ok",
        message="Profile updated",
        data=UserProfile.model_validate(user).model_dump(mode="json"),
    )


@router.put("/me/password", response_model=ApiResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(_auth_service),
) -> ApiResponse:
    """Change the authenticated user's password."""
    user_id = UUID(current_user["sub"])
    with _handle_domain_errors():
        service.change_password(
            user_id=user_id,
            old_password=body.old_password,
            new_password=body.new_password,
        )
    return ApiResponse(status="ok", message="Password changed successfully")
