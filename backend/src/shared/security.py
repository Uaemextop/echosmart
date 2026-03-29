"""Password hashing and JWT token management.

Centralises all crypto operations so that feature modules never
deal with raw secrets, algorithms, or token encoding directly.

Internals
---------
- **Passwords**: bcrypt via ``passlib`` — automatic salt, configurable rounds.
- **Tokens**: HS256 JWTs via ``python-jose`` — short-lived access tokens plus
  long-lived refresh tokens.

Typical usage::

    from src.shared.security import hash_password, verify_password, create_access_token

    hashed = hash_password("hunter2")
    assert verify_password("hunter2", hashed)

    token = create_access_token({"sub": str(user.id), "role": "admin"})
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings
from src.shared.exceptions import AuthenticationError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*.

    Args:
        password: The plaintext password to hash.

    Returns:
        The hashed password string (bcrypt encoding).
    """
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify *plain_password* against a stored bcrypt hash.

    Args:
        plain_password: The candidate plaintext password.
        hashed_password: The stored bcrypt hash.

    Returns:
        ``True`` if the password matches.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a short-lived JWT access token.

    The token includes an ``exp`` claim computed from *expires_delta* or
    the configured default (``jwt_access_token_expire_minutes``).

    Args:
        data: Claims to embed in the token (must include ``"sub"``).
        expires_delta: Optional custom lifetime; falls back to settings.

    Returns:
        An encoded JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
    to_encode.update({"exp": expire, "iat": now, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token.

    The lifetime is controlled by ``jwt_refresh_token_expire_days`` in
    settings.  The token carries a ``"type": "refresh"`` claim so that
    access and refresh tokens cannot be swapped.

    Args:
        data: Claims to embed (must include ``"sub"``).

    Returns:
        An encoded JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "iat": now, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: The raw JWT string.

    Returns:
        The decoded claims dictionary.

    Raises:
        AuthenticationError: If the token is invalid, expired, or
            malformed.
    """
    try:
        payload: dict = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("sub") is None:
            raise AuthenticationError("Token is missing 'sub' claim")
        return payload
    except JWTError as exc:
        raise AuthenticationError(f"Token validation failed: {exc}") from exc
