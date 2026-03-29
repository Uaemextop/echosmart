"""Router HTTP para health checks del backend."""

from fastapi import APIRouter, Depends

from src.health.schemas import HealthCheckResponse, RootStatusResponse
from src.health.service import HealthService, get_health_service

router = APIRouter(tags=["Health"])


@router.get("/", response_model=RootStatusResponse)
async def root(
    health_service: HealthService = Depends(get_health_service),
) -> RootStatusResponse:
    """Responder el estado base del servicio."""
    return health_service.get_root_status()


@router.get("/health", response_model=HealthCheckResponse)
@router.get(
    "/api/v1/health",
    response_model=HealthCheckResponse,
    include_in_schema=False,
)
async def health_check(
    health_service: HealthService = Depends(get_health_service),
) -> HealthCheckResponse:
    """Responder el health check del servicio."""
    return health_service.get_health_status()
