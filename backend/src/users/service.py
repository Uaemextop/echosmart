"""User management service — admin business logic and use cases.

``UserManagementService`` orchestrates administrative user operations:

- User CRUD (create, read, update, deactivate).
- Role changes.
- Paginated listing and search.

**Transaction policy:** The service owns ``commit`` / ``rollback``
because write operations must be atomic.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from src.models.user import User
from src.shared.exceptions import ConflictError, NotFoundError, ValidationError
from src.shared.pagination import PaginatedResponse, PaginationParams
from src.shared.security import hash_password
from src.users.repository import AdminUserRepository


class UserManagementService:
    """High-level admin user-management orchestrator.

    Args:
        db: An active SQLAlchemy session — the service manages
            ``commit`` and ``rollback`` internally.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = AdminUserRepository(db)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_users(
        self,
        tenant_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse:
        """List users for a tenant with pagination.

        Args:
            tenant_id: The tenant's primary key.
            pagination: Page / sort parameters.

        Returns:
            A :class:`PaginatedResponse` containing user records.
        """
        total = self._repo.count_by_tenant(tenant_id)
        users = self._repo.get_all(
            skip=pagination.offset,
            limit=pagination.per_page,
            filters={"tenant_id": tenant_id},
        )
        return PaginatedResponse.build(
            items=users,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
        )

    def get_user(self, user_id: UUID) -> User:
        """Retrieve a single user by ID.

        Args:
            user_id: The user's primary key.

        Returns:
            The :class:`User` instance.

        Raises:
            NotFoundError: If no user matches the given ID.
        """
        return self._repo.get_by_id_or_raise(user_id)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def create_user(self, tenant_id: UUID, data: dict) -> User:
        """Create a new user within a tenant.

        The password is hashed before storage. Duplicate email
        addresses are rejected.

        Args:
            tenant_id: Owning tenant's primary key.
            data: Validated user attributes (from ``UserCreate``).

        Returns:
            The newly persisted :class:`User`.

        Raises:
            ConflictError: If the email is already in use.
        """
        # Check for duplicate email
        existing = (
            self.db.query(User)
            .filter(User.email == data["email"])
            .first()
        )
        if existing:
            raise ConflictError("User", f"email '{data['email']}' is already registered")

        data["tenant_id"] = tenant_id
        data["hashed_password"] = hash_password(data.pop("password"))

        user = self._repo.create(data)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: UUID, data: dict) -> User:
        """Update an existing user.

        Only the keys present in *data* are modified.

        Args:
            user_id: The user's primary key.
            data: Partial update attributes (from ``UserUpdate``).

        Returns:
            The updated :class:`User`.

        Raises:
            NotFoundError: If the user does not exist.
        """
        self._repo.get_by_id_or_raise(user_id)
        updated = self._repo.update(user_id, data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user account.

        Sets ``is_active`` to ``False``.  The user can no longer
        authenticate until reactivated.

        Args:
            user_id: The user's primary key.

        Returns:
            The deactivated :class:`User`.

        Raises:
            NotFoundError: If the user does not exist.
        """
        self._repo.get_by_id_or_raise(user_id)
        updated = self._repo.update(user_id, {"is_active": False})
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def change_role(self, user_id: UUID, new_role: str) -> User:
        """Change a user's role.

        Args:
            user_id: The user's primary key.
            new_role: The new role to assign (e.g. ``"admin"``,
                ``"user"``).

        Returns:
            The updated :class:`User`.

        Raises:
            NotFoundError: If the user does not exist.
            ValidationError: If the role is invalid.
        """
        allowed = {"admin", "user"}
        if new_role not in allowed:
            raise ValidationError(
                f"Role must be one of: {', '.join(sorted(allowed))}",
                field="role",
            )

        self._repo.get_by_id_or_raise(user_id)
        updated = self._repo.update(user_id, {"role": new_role})
        self.db.commit()
        self.db.refresh(updated)
        return updated
