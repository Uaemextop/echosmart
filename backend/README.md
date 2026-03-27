# EchoSmart — Backend (FastAPI)

API REST y servicios cloud para la plataforma EchoSmart.

## Stack

- **Framework**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0+
- **Validación**: Pydantic 2.0+
- **Base de datos**: PostgreSQL 14+ · InfluxDB 2.7+ · Redis 7+
- **Auth**: JWT con RBAC
- **Workers**: Celery 5.3+
- **Testing**: pytest 7.4+

## Inicio Rápido

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Docs

Con el servidor en ejecución, visitar `http://localhost:8000/docs` para la documentación interactiva (Swagger UI).

## Tests

```bash
pytest tests/ -v --cov=src
```

## Estructura

```
backend/
├── src/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración (env vars)
│   ├── database.py          # Conexión a bases de datos
│   ├── dependencies.py      # Inyección de dependencias
│   ├── routers/             # Endpoints REST
│   ├── services/            # Lógica de negocio
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Esquemas Pydantic
│   ├── middleware/          # Middlewares
│   ├── workers/             # Tareas asincrónicas
│   └── websocket/           # WebSocket tiempo real
├── migrations/              # Migraciones Alembic
├── tests/                   # Tests
├── requirements.txt
├── Dockerfile
└── .env.example
```
