"""Exception hierarchy for the EchoSmart platform.

Defines a structured exception tree that maps cleanly to HTTP status codes.
All exceptions inherit from ``EchoSmartError`` so callers can catch the
entire family with a single ``except`` block when needed.

Typical usage::

    from src.shared.exceptions import NotFoundError

    def get_sensor(sensor_id: UUID) -> Sensor:
        sensor = db.query(Sensor).get(sensor_id)
        if sensor is None:
            raise NotFoundError("Sensor", str(sensor_id))
        return sensor
"""

from __future__ import annotations


class EchoSmartError(Exception):
    """Base exception for all EchoSmart domain errors.

    Attributes:
        message: Human-readable description of the error.
        code: Machine-readable error code for API consumers.
    """

    def __init__(self, message: str = "An unexpected error occurred", code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(EchoSmartError):
    """Raised when a requested resource does not exist.

    Maps to HTTP 404.

    Args:
        resource: Name of the resource type (e.g. ``"Sensor"``).
        resource_id: Identifier that was looked up.
    """

    def __init__(self, resource: str, resource_id: str) -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            code="NOT_FOUND",
        )


class ValidationError(EchoSmartError):
    """Raised when input data fails domain-level validation.

    Maps to HTTP 422.

    Args:
        message: Description of what failed validation.
        field: Optional field name that caused the error.
    """

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        prefix = f"[{field}] " if field else ""
        super().__init__(
            message=f"{prefix}{message}",
            code="VALIDATION_ERROR",
        )


class AuthenticationError(EchoSmartError):
    """Raised when credentials are missing or invalid.

    Maps to HTTP 401.
    """

    def __init__(self, message: str = "Invalid or expired credentials") -> None:
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(EchoSmartError):
    """Raised when the authenticated user lacks the required permission.

    Maps to HTTP 403.
    """

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class ConflictError(EchoSmartError):
    """Raised when an operation conflicts with existing state.

    Maps to HTTP 409.  Common causes: duplicate email, unique constraint
    violations, or optimistic-lock failures.

    Args:
        resource: Name of the resource type.
        detail: What caused the conflict.
    """

    def __init__(self, resource: str, detail: str) -> None:
        self.resource = resource
        super().__init__(
            message=f"{resource} conflict: {detail}",
            code="CONFLICT",
        )


class RateLimitError(EchoSmartError):
    """Raised when a client exceeds the allowed request rate.

    Maps to HTTP 429.

    Args:
        retry_after: Seconds the client should wait before retrying.
    """

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            code="RATE_LIMIT_EXCEEDED",
        )
