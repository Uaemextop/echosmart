"""Servicios de health check del backend."""

from src.config import settings
from src.health.schemas import HealthCheckResponse, RootStatusResponse


class HealthService:
    """Proveer respuestas de estado del servicio."""

    def get_root_status(self) -> RootStatusResponse:
        """Construir la respuesta del endpoint raíz."""
        return RootStatusResponse(
            status="ok",
            service=settings.app_service_name,
            version=settings.app_version,
        )

    def get_health_status(self) -> HealthCheckResponse:
        """Construir la respuesta del health check."""
        return HealthCheckResponse(status="healthy")


def get_health_service() -> HealthService:
    """Resolver la dependencia del servicio de health."""
    return HealthService()
