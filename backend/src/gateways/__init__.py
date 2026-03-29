"""Gateway management feature module.

Handles the full lifecycle of IoT gateways:

- CRUD operations on :class:`~src.models.gateway.Gateway` entities.
- API key generation and lookup for device authentication.
- Heartbeat tracking and online/offline status management.

Public surface re-exported for convenience::

    from src.gateways import GatewayService, GatewayRepository
    from src.gateways.router import router as gateways_router
"""

from src.gateways.repository import GatewayRepository
from src.gateways.service import GatewayService

__all__ = [
    "GatewayRepository",
    "GatewayService",
]
