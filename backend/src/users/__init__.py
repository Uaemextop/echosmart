"""User management (admin) feature module.

Provides administrative operations for managing users within a tenant:

- CRUD operations on :class:`~src.models.user.User` entities.
- Role management and user deactivation.
- Search and filtering.

Public surface re-exported for convenience::

    from src.users import UserManagementService, AdminUserRepository
    from src.users.router import router as users_router
"""

from src.users.repository import AdminUserRepository
from src.users.service import UserManagementService

__all__ = [
    "AdminUserRepository",
    "UserManagementService",
]
