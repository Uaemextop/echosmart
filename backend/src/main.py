"""EchoSmart Backend — Punto de entrada FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

app = FastAPI(
    title="EchoSmart API",
    description="API REST para la plataforma IoT de monitoreo ambiental en invernaderos.",
    version="1.0.0",
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


@app.get("/", tags=["Health"])
async def root():
    """Health check del servicio."""
    return {"status": "ok", "service": "echosmart-backend", "version": "1.0.0"}


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Endpoint de health check para monitoreo."""
    return {"status": "healthy"}
