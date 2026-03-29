"""Router de alertas — /api/v1/alerts/*.

Re-exports the fully implemented router from the ``alerts`` feature
module so that ``src.main`` continues to work via::

    from src.routers import alerts
    app.include_router(alerts.router)
"""

from src.alerts.router import router  # noqa: F401

__all__ = ["router"]
