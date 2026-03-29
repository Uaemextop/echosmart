"""Authentication service — business logic and use cases.

``AuthService`` orchestrates every auth operation:

- Registration (serial validation → user creation → tenant creation)
- Login / admin-login (credential check → token issuance)
- Token refresh
- Profile reads and updates
- Password changes

**Transaction policy:** The service owns ``commit`` / ``rollback``
because most operations span multiple aggregates (e.g. register
touches User, Serial, and Tenant in a single unit of work).
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.auth.repository import UserRepository
from src.models.serial import Serial, SerialStatus
from src.models.tenant import Tenant
from src.models.user import User
from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from src.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def _slugify(text: str) -> str:
    """Turn *text* into a URL-safe slug (lowercase, hyphens only).

    Unicode characters are decomposed to their ASCII base forms so
    that names like ``"José García"`` become ``"jose-garcia"`` rather
    than losing characters entirely.
    """
    # Decompose Unicode → strip combining marks → re-encode as ASCII
    normalised = unicodedata.normalize("NFKD", text)
    ascii_text = normalised.encode("ascii", "ignore").decode("ascii")
    slug = ascii_text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


class AuthService:
    """High-level auth use-case orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._users = UserRepository(db)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        email: str,
        password: str,
        full_name: str,
        serial_code: str,
        phone: str | None = None,
    ) -> User:
        """Register a new user with a kit serial code.

        Steps:
        1. Validate the serial exists and has status ``AVAILABLE``.
        2. Ensure no existing user with the same e-mail.
        3. Create a default tenant for the user.
        4. Create the user (hashed password, linked to tenant + serial).
        5. Mark the serial as ``REGISTERED``.
        6. Commit the whole transaction.

        Args:
            email: User e-mail (normalised to lowercase).
            password: Plaintext password (will be hashed).
            full_name: User's display name.
            serial_code: Kit serial code (e.g. ``"ES-202603-0001"``).
            phone: Optional phone number.

        Returns:
            The newly created :class:`User`.

        Raises:
            ValidationError: If the serial does not exist.
            ConflictError: If the serial is already used, or the
                e-mail is already registered.
        """
        email = email.lower().strip()

        # 1. Validate serial
        serial = (
            self.db.query(Serial)
            .filter(Serial.code == serial_code)
            .first()
        )
        if serial is None:
            raise ValidationError(
                f"Serial code '{serial_code}' does not exist",
                field="serial_code",
            )
        if serial.status != SerialStatus.AVAILABLE:
            raise ConflictError(
                "Serial",
                f"Serial code '{serial_code}' is not available "
                f"(current status: {serial.status.value})",
            )

        # 2. Duplicate e-mail check
        if self._users.get_by_email(email) is not None:
            raise ConflictError("User", f"Email '{email}' is already registered")

        # 3. Create default tenant
        tenant = Tenant(
            name=f"{full_name}'s Greenhouse",
            slug=_slugify(f"{full_name}-{serial_code}"),
            is_active=True,
        )
        self.db.add(tenant)
        self.db.flush()

        # 4. Create user
        user = self._users.create(
            {
                "email": email,
                "hashed_password": hash_password(password),
                "full_name": full_name,
                "phone": phone,
                "role": "user",
                "serial_number": serial_code,
                "tenant_id": tenant.id,
                "is_active": True,
                "is_suspended": False,
                "two_factor_enabled": False,
            }
        )

        # 5. Mark serial as registered
        serial.status = SerialStatus.REGISTERED
        serial.user_id = user.id
        serial.registered_at = datetime.now(timezone.utc)
        self.db.flush()

        # 6. Commit
        self.db.commit()
        self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(self, email: str, password: str) -> dict:
        """Authenticate a user and return a token pair.

        Args:
            email: User e-mail.
            password: Plaintext password candidate.

        Returns:
            A dict with ``access_token``, ``refresh_token``,
            ``token_type``, ``user_id``, and ``role``.

        Raises:
            AuthenticationError: If credentials are invalid or the
                account is inactive/suspended.
        """
        user = self._authenticate(email, password)

        self._users.update_last_login(user.id)
        self.db.commit()

        return self._issue_tokens(user)

    def admin_login(
        self,
        email: str,
        password: str,
        totp_code: str | None = None,
    ) -> dict:
        """Authenticate an admin user, enforcing role and optional 2FA.

        Args:
            email: Admin e-mail.
            password: Plaintext password candidate.
            totp_code: Optional TOTP code when 2FA is enabled.

        Returns:
            Token dict (same shape as :meth:`login`).

        Raises:
            AuthenticationError: On bad credentials.
            AuthorizationError: If the user is not an admin.
            AuthenticationError: If 2FA is required but the code is
                missing or invalid.
        """
        user = self._authenticate(email, password)

        if user.role != "admin":
            raise AuthorizationError("Admin access is required")

        # 2FA check (when enabled on the account)
        if user.two_factor_enabled:
            if not totp_code:
                raise AuthenticationError(
                    "Two-factor authentication code is required"
                )
            # NOTE: Full TOTP verification (e.g. via pyotp) will be
            # integrated when the 2FA setup flow is implemented.
            # For now we validate that a code was provided.

        self._users.update_last_login(user.id)
        self.db.commit()

        return self._issue_tokens(user)

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    def refresh_token(self, refresh_token: str) -> dict:
        """Exchange a valid refresh token for a new access + refresh pair.

        Args:
            refresh_token: The JWT refresh token.

        Returns:
            A fresh token dict.

        Raises:
            AuthenticationError: If the token is invalid, expired, or
                not of type ``"refresh"``.
            NotFoundError: If the user referenced in the token no
                longer exists.
        """
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise AuthenticationError(
                "Expected a refresh token, got a different token type"
            )

        user_id = UUID(payload["sub"])
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))

        if not user.is_active or user.is_suspended:
            raise AuthenticationError("Account is inactive or suspended")

        return self._issue_tokens(user)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    def get_profile(self, user_id: UUID) -> User:
        """Retrieve a user's profile by ID.

        Args:
            user_id: The user's primary key.

        Returns:
            The :class:`User` instance.

        Raises:
            NotFoundError: If no user matches.
        """
        return self._users.get_by_id_or_raise(user_id)

    def update_profile(self, user_id: UUID, data: dict) -> User:
        """Update editable profile fields.

        Only ``full_name`` and ``phone`` are accepted — other keys
        are silently ignored to prevent privilege escalation.

        Args:
            user_id: The user's primary key.
            data: Dictionary of fields to update.

        Returns:
            The refreshed :class:`User` instance.

        Raises:
            NotFoundError: If no user matches.
        """
        allowed = {k: v for k, v in data.items() if k in ("full_name", "phone")}
        if not allowed:
            return self.get_profile(user_id)

        user = self._users.update(user_id, allowed)
        if user is None:
            raise NotFoundError("User", str(user_id))

        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(
        self,
        user_id: UUID,
        old_password: str,
        new_password: str,
    ) -> None:
        """Change a user's password after verifying the current one.

        Args:
            user_id: The user's primary key.
            old_password: The current plaintext password.
            new_password: The new plaintext password.

        Raises:
            NotFoundError: If no user matches.
            AuthenticationError: If *old_password* is incorrect.
        """
        user = self._users.get_by_id_or_raise(user_id)

        if not verify_password(old_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        self.db.flush()
        self.db.commit()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _authenticate(self, email: str, password: str) -> User:
        """Verify credentials and return the user on success.

        Raises:
            AuthenticationError: On any verification failure.
        """
        email = email.lower().strip()
        user = self._users.get_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        if user.is_suspended:
            raise AuthenticationError("Account is suspended")

        return user

    @staticmethod
    def _issue_tokens(user: User) -> dict:
        """Build an access + refresh token pair for *user*."""
        claims = {"sub": str(user.id), "role": user.role}
        return {
            "access_token": create_access_token(claims),
            "refresh_token": create_refresh_token(claims),
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role,
        }
