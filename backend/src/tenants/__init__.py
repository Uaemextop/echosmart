"""Tenant management feature module.

Provides operations for managing tenant settings and branding:

- Tenant profile retrieval and updates.
- Branding customisation.
- Usage statistics.

Public surface re-exported for convenience::

    from src.tenants import TenantService, TenantRepository
    from src.tenants.router import router as tenants_router
"""

from src.tenants.repository import TenantRepository
from src.tenants.service import TenantService

__all__ = [
    "TenantRepository",
    "TenantService",
]
