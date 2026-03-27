# EchoSmart — Infraestructura Local de Desarrollo

Guía para levantar el entorno completo de desarrollo con UN SOLO COMANDO, incluyendo todos los servicios, emuladores de sensores, y datos de demo.

---

## 1. Requisitos

| Herramienta | Versión Mínima | Verificar |
|-------------|---------------|-----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| Git | 2.30+ | `git --version` |
| Make | 4+ | `make --version` |

---

## 2. Setup Rápido (Un Solo Comando)

```bash
# Clonar el repositorio
git clone https://github.com/Uaemextop/echosmart.git
cd echosmart

# Levantar TODO el entorno de desarrollo
make setup
```

### ¿Qué hace `make setup`?

1. ✅ Verifica prerequisitos (Docker, Python, Node.js)
2. ✅ Genera archivos `.env` desde templates
3. ✅ Genera claves JWT y certificados SSL para desarrollo
4. ✅ Construye imágenes Docker
5. ✅ Levanta todos los servicios (PostgreSQL, InfluxDB, Redis, Mosquitto, Backend, Frontend, Nginx)
6. ✅ Levanta emulador de sensores
7. ✅ Ejecuta migraciones de base de datos
8. ✅ Carga datos de demo (tenant, usuarios, gateways, sensores, lecturas históricas)
9. ✅ Verifica conectividad entre servicios
10. ✅ Imprime URLs de acceso y credenciales

### Output Esperado

```
╔══════════════════════════════════════════════════════╗
║  🌱 EchoSmart Development Environment               ║
║  Todos los servicios están corriendo                 ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Frontend:  http://localhost:3000                     ║
║  Backend:   http://localhost:8000                     ║
║  API Docs:  http://localhost:8000/docs                ║
║  Adminer:   http://localhost:8080                     ║
║  Mailhog:   http://localhost:8025                     ║
║  Grafana:   http://localhost:3001                     ║
║                                                      ║
║  Credenciales de desarrollo:                         ║
║    Admin: admin@echosmart.local / admin123            ║
║    Operator: operator@echosmart.local / operator123   ║
║    Viewer: viewer@echosmart.local / viewer123         ║
║                                                      ║
║  Emulador de sensores: ACTIVO                        ║
║    Gateway emulado: gw-emulator-01                   ║
║    5 sensores generando datos cada 10 segundos       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

## 3. Comandos del Makefile

```bash
# === Lifecycle ===
make setup          # Setup completo del entorno (primera vez)
make up             # Levantar todos los servicios
make down           # Detener todos los servicios
make restart        # Reiniciar servicios
make clean          # Limpiar todo (volúmenes, cache, imágenes)

# === Desarrollo ===
make logs           # Ver logs de todos los servicios
make logs-backend   # Logs solo del backend
make logs-frontend  # Logs solo del frontend
make shell-backend  # Shell interactivo en el contenedor del backend
make shell-db       # Shell de PostgreSQL

# === Testing ===
make test           # Ejecutar TODOS los tests
make test-backend   # Tests backend con coverage
make test-frontend  # Tests frontend con coverage
make test-gateway   # Tests gateway con coverage

# === Calidad ===
make lint           # Linting de todos los componentes
make format         # Formatear código (black + prettier)
make type-check     # Type checking (mypy + tsc)

# === Base de datos ===
make migrate        # Ejecutar migraciones de Alembic
make seed           # Cargar datos de demo
make reset-db       # Resetear base de datos

# === Emulador ===
make emulator-status              # Estado del emulador
make emulator-scenario S=normal   # Escenario normal (24h en 10 min)
make emulator-scenario S=heat     # Simular ola de calor
make emulator-scenario S=frost    # Simular helada
make emulator-scenario S=failure  # Simular sensor desconectado

# === Build ===
make build          # Build de producción
make iso-server     # Generar ISO del servidor
make iso-gateway    # Generar imagen del RPi gateway

# === Ayuda ===
make help           # Mostrar todos los comandos disponibles
```

---

## 4. Servicios del Entorno de Desarrollo

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| Frontend (React) | 3000 | http://localhost:3000 | App web con HMR |
| Backend (FastAPI) | 8000 | http://localhost:8000 | API REST + WebSocket |
| API Docs | 8000 | http://localhost:8000/docs | Swagger UI interactivo |
| PostgreSQL | 5432 | — | Base de datos relacional |
| InfluxDB | 8086 | http://localhost:8086 | Base de datos temporal |
| Redis | 6379 | — | Cache + pub/sub |
| Mosquitto | 1883 / 9001 | — | Broker MQTT + WebSocket |
| Nginx | 80 / 443 | https://localhost | Reverse proxy con SSL |
| Adminer | 8080 | http://localhost:8080 | UI de PostgreSQL |
| Mailhog | 8025 / 1025 | http://localhost:8025 | Captura de emails |
| Grafana | 3001 | http://localhost:3001 | Dashboards de monitoreo |
| Emulador | — | — | Genera datos de 5 sensores |

---

## 5. Emulador de Sensores

El emulador genera datos realistas de los 5 sensores del invernadero, publicándolos vía MQTT como si fuera un gateway real.

### Comportamiento por Defecto

| Sensor | Rango | Variación | Frecuencia |
|--------|-------|-----------|------------|
| Temperatura | 18–32°C | Sinusoidal (ciclo día/noche) | 10 seg |
| Humedad | 55–85% | Inversa a temperatura | 10 seg |
| Luminosidad | 0–50,000 lux | Ciclo día/noche con nubes | 10 seg |
| Humedad Suelo | 30–80% | Degradación gradual | 10 seg |
| CO₂ | 350–1200 ppm | Picos nocturnos | 10 seg |

### Escenarios Predefinidos

```bash
# Simular un día completo en 10 minutos
make emulator-scenario S=normal

# Simular ola de calor (temperatura sube a 45°C)
make emulator-scenario S=heat

# Simular helada (temperatura baja a -2°C)
make emulator-scenario S=frost

# Simular fallo de sensor (un sensor deja de responder)
make emulator-scenario S=failure

# Simular corte de red (gateway se desconecta 10 min)
make emulator-scenario S=network-outage
```

### API del Emulador

```bash
# Ver estado actual
curl http://localhost:9090/emulator/status

# Cambiar escenario en runtime
curl -X POST http://localhost:9090/emulator/scenario -d '{"name": "heat-wave"}'

# Pausar/resumir
curl -X POST http://localhost:9090/emulator/pause
curl -X POST http://localhost:9090/emulator/resume
```

---

## 6. Flujo de Datos en Desarrollo

```
Emulador de Sensores
    │
    │ MQTT: echosmart/gw-emulator-01/sensor/{type}
    ▼
Mosquitto (MQTT Broker) ──────────────────┐
    │                                      │
    │ MQTT subscribe                       │ WebSocket
    ▼                                      ▼
Backend (FastAPI)                    Frontend (React)
    │                                      │
    │ SQL / HTTP                           │ Actualización
    ▼                                      │ en tiempo real
PostgreSQL + InfluxDB                      ▼
    │                                Dashboard con
    │ Evaluación de alertas         gráficas en vivo
    ▼
Alert Engine → Mailhog (captura emails)
```

---

## 7. Resolución de Problemas

### Puerto ocupado

```bash
# Encontrar qué proceso usa el puerto
sudo lsof -i :8000
# Detener el proceso o cambiar el puerto en .env
```

### Contenedor no inicia

```bash
# Ver logs del contenedor
docker compose -f docker-compose.dev.yml logs [servicio]

# Reconstruir imagen
docker compose -f docker-compose.dev.yml build [servicio]
```

### Resetear todo

```bash
make clean    # Elimina volúmenes, contenedores, imágenes
make setup    # Re-crear todo desde cero
```

---

*Volver al [Índice de Documentación](README.md)*
