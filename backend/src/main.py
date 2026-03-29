"""EchoSmart Backend — Punto de entrada FastAPI.

Software propietario para la plataforma IoT de monitoreo
ambiental en invernaderos inteligentes.

Arquitectura: Clean Architecture (feature-based modules).
Cada feature (auth, sensors, alerts, …) encapsula su propio
router, service, repository y schemas.

Dos binarios:
- echosmart: gateway EchoPy (Raspberry Pi)
- echosmart-server: servidor backend
"""

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    EchoSmartError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

# Feature-based routers (Clean Architecture)
from src.auth.router import router as auth_router
from src.sensors.router import router as sensors_router
from src.alerts.router import router as alerts_router
from src.gateways.router import router as gateways_router
from src.reports.router import router as reports_router
from src.users.router import router as users_router
from src.tenants.router import router as tenants_router

# Legacy routers (serials, echopy, updates — not yet migrated)
from src.routers import serials, echopy, updates

app = FastAPI(
    title="EchoSmart API",
    description=(
        "API REST para la plataforma IoT de monitoreo ambiental en invernaderos.\n\n"
        "**Software propietario** — Todos los derechos reservados.\n\n"
        "## Módulos\n"
        "- **Auth**: Registro con serial del kit, login usuario/admin, 2FA\n"
        "- **Serials**: Gestión de números de serie para kits EchoPy\n"
        "- **EchoPy**: Gestión de dispositivos EchoPy (gateway RPi)\n"
        "- **Sensors**: Monitoreo de sensores del invernadero\n"
        "- **Alerts**: Motor de alertas y notificaciones\n"
        "- **Gateways**: Gestión de gateways IoT\n"
        "- **Reports**: Generación de reportes PDF/Excel\n"
        "- **Users**: Gestión de usuarios (admin)\n"
        "- **Tenants**: Gestión multi-tenant\n"
        "- **Updates**: Sistema de actualizaciones Cosmuodate\n"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------
# Global exception handler — maps domain exceptions to HTTP responses
# ------------------------------------------------------------------

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    NotFoundError: 404,
    ValidationError: 422,
    AuthenticationError: 401,
    AuthorizationError: 403,
    ConflictError: 409,
    RateLimitError: 429,
}


@app.exception_handler(EchoSmartError)
async def echosmart_exception_handler(request: Request, exc: EchoSmartError) -> JSONResponse:
    """Convert domain exceptions to structured JSON error responses."""
    status_code = _EXCEPTION_STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "code": exc.code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Register routers — feature-based modules
# ------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(sensors_router)
app.include_router(alerts_router)
app.include_router(gateways_router)
app.include_router(reports_router)
app.include_router(users_router)
app.include_router(tenants_router)

# Legacy routers (pending migration to feature modules)
app.include_router(serials.router)
app.include_router(echopy.router)
app.include_router(updates.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check del servicio."""
    return {
        "status": "ok",
        "service": "echosmart-server",
        "version": "2.0.0",
        "modules": [
            "auth", "serials", "echopy", "updates",
            "sensors", "gateways", "alerts", "reports",
        ],
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Endpoint de health check para monitoreo."""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "up",
            "redis": "up",
            "mqtt": "up",
        },
    }
