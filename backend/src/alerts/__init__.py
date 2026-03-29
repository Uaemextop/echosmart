"""Alert management feature module.

Handles the lifecycle of IoT alert rules and triggered alerts:

- Creation and management of alert rules per sensor.
- Automatic evaluation of sensor readings against rules.
- Acknowledgement and resolution workflows.
- Severity-based filtering and statistics.

Public surface re-exported for convenience::

    from src.alerts import AlertService, AlertRepository
    from src.alerts.router import router as alerts_router
"""

from src.alerts.repository import AlertRepository
from src.alerts.service import AlertService

__all__ = [
    "AlertRepository",
    "AlertService",
]
