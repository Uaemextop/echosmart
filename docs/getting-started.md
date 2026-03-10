# EchoSmart — Primeros Pasos

Guía para configurar el entorno de desarrollo y poner en marcha la plataforma EchoSmart.

---

## Requisitos Previos

### Software

| Componente | Versión Mínima |
|------------|---------------|
| Python | 3.9+ |
| Node.js | 18+ |
| Docker & Docker Compose | 20+ / 2.x |
| Git | 2.x |

### Hardware (para el Gateway)

| Componente | Especificación |
|------------|---------------|
| Raspberry Pi | 4B con 4 GB de RAM |
| Fuente de alimentación | 5 V / 3 A USB-C |
| Tarjeta SD | 32 GB Class 10 |
| Sensores | Según necesidad (ver [Sensores y Hardware](sensors-hardware.md)) |

---

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart
```

### 2. Levantar la Infraestructura con Docker

```bash
docker-compose up -d
```

Esto inicia los servicios de base de datos y mensajería:

| Servicio | Puerto |
|----------|--------|
| PostgreSQL | 5432 |
| InfluxDB | 8086 |
| Redis | 6379 |
| Mosquitto (MQTT) | 1883 |

### 3. Configurar el Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

Copiar y editar las variables de entorno:

```bash
cp .env.example .env
# Editar .env con las credenciales de base de datos y JWT_SECRET_KEY
```

Iniciar el servidor:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000` y la documentación interactiva de la API en `http://localhost:8000/docs`.

### 4. Configurar el Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`.

### 5. Configurar el Gateway (Raspberry Pi)

```bash
cd gateway
pip install -r requirements.txt
cp .env.example .env
# Editar .env con GATEWAY_ID, CLOUD_API_URL y CLOUD_API_KEY
python main.py
```

Para más detalles sobre la configuración del gateway, consultar [Gateway y Edge Computing](gateway-edge-computing.md).

---

## Variables de Entorno Principales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/echosmart` |
| `INFLUXDB_URL` | Conexión a InfluxDB | `http://localhost:8086` |
| `INFLUXDB_TOKEN` | Token de acceso a InfluxDB | `my-token` |
| `REDIS_URL` | Conexión a Redis | `redis://localhost:6379` |
| `JWT_SECRET_KEY` | Clave secreta para JWT | `cambiar-en-produccion` |
| `GATEWAY_ID` | Identificador del gateway | `gw-001` |
| `CLOUD_API_URL` | URL del backend cloud | `https://api.echosmart.io` |

---

## Verificación

1. **Backend**: Abrir `http://localhost:8000/docs` y verificar que los endpoints respondan.
2. **Frontend**: Abrir `http://localhost:3000` y verificar que el dashboard cargue.
3. **Gateway**: Revisar la salida de `python main.py` y confirmar lecturas de sensores.

---

## Siguientes Pasos

- Revisar la [Funcionalidad de la Aplicación](app-functionality.md) para entender las capacidades del sistema.
- Consultar el [Roadmap Ejecutivo](roadmap.md) para entender las fases del proyecto.
- Explorar la [Arquitectura de Software](architecture.md) para comprender el diseño del sistema.

---

*Volver al [Índice de Documentación](README.md)*
