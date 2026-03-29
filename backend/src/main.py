"""EchoSmart Backend — Punto de entrada FastAPI.

Software propietario para la plataforma IoT de monitoreo
ambiental en invernaderos inteligentes.

Dos binarios:
- echosmart: gateway EchoPy (Raspberry Pi)
- echosmart-server: servidor backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import auth, sensors, gateways, alerts, reports, users, tenants
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
        "- **Updates**: Sistema de actualizaciones Cosmuodate\n"
        "- **Gateways**: Gestión de gateways (compatibilidad)\n"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registrar routers ---
app.include_router(auth.router)
app.include_router(serials.router)
app.include_router(echopy.router)
app.include_router(updates.router)
app.include_router(sensors.router)
app.include_router(gateways.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(tenants.router)


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
