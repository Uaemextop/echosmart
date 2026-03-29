"""Authentication feature module for EchoSmart.

Handles the complete auth lifecycle:

- **Registration** with serial-code validation
- **Login** for regular users and admins (with optional 2FA)
- **JWT management** — access + refresh token pairs
- **Profile** retrieval and updates
- **Password** changes and reset flows

Architecture
------------
::

    router  ─→  service  ─→  repository  ─→  shared (DB / security)
      │                          │
      └── schemas (DTOs)         └── BaseRepository[User]

The router is intentionally *thin*: it parses the HTTP request into
a schema, delegates to ``AuthService``, and wraps the result in the
standard ``ApiResponse`` envelope.

Quick start::

    from src.auth.router import router as auth_router

    app.include_router(auth_router)
"""

from src.auth.router import router
from src.auth.service import AuthService

__all__ = [
    "router",
    "AuthService",
]
