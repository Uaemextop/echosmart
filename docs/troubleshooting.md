# EchoSmart — Resolución de Problemas

Guía de diagnóstico y solución para los problemas más frecuentes en cada capa de la plataforma.

---

## 1. Gateway (Raspberry Pi)

### 1.1 No se detectan sensores

**Síntoma:** El gateway arranca pero no lee ningún sensor.

**Diagnóstico:**

```bash
# Verificar interfaces habilitadas
sudo raspi-config nonint get_i2c    # 0 = habilitado
ls /sys/bus/w1/devices/             # Dispositivos 1-Wire
ls /dev/serial0                     # UART
```

**Soluciones:**

| Causa | Solución |
|-------|---------|
| Interfaz no habilitada | Ejecutar `sudo raspi-config` y habilitar I2C / 1-Wire / Serial |
| Device tree no configurado | Verificar `/boot/firmware/config.txt` (ver [Raspberry Pi Setup](raspberry-pi-setup.md)) |
| Sensor desconectado | Revisar cableado y resistores pull-up |
| Permisos insuficientes | `sudo usermod -aG gpio,i2c,dialout $USER` y reconectar |

### 1.2 Error "Permission denied" en GPIO

```bash
# Verificar grupos del usuario
groups
# Debe incluir: gpio i2c dialout

# Si no están:
sudo usermod -aG gpio,i2c,dialout $USER
# Cerrar sesión SSH y reconectar
```

### 1.3 Lecturas de sensor con valor `None` o `-999`

| Sensor | Causa Probable | Solución |
|--------|---------------|---------|
| DS18B20 | Resistor pull-up faltante | Agregar 4.7 kΩ entre VDD y DQ |
| DHT22 | Lectura demasiado frecuente | Esperar mínimo 2 s entre lecturas |
| BH1750 | Dirección I2C incorrecta | Verificar con `i2cdetect -y 1` |
| MHZ-19C | UART no configurado | Deshabilitar consola serial en `raspi-config` |
| Soil Moisture | Canal ADC incorrecto | Verificar canal en `sensors.json` |

### 1.4 Mosquitto no inicia

```bash
# Revisar logs
journalctl -u mosquitto -n 50

# Verificar que el puerto 1883 no esté ocupado
sudo ss -tlnp | grep 1883

# Verificar configuración
mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

### 1.5 Falla en la sincronización con la nube

```bash
# Verificar conectividad
curl -s https://api.echosmart.io/health

# Verificar API key
curl -s -H "Authorization: Bearer $CLOUD_API_KEY" \
  https://api.echosmart.io/api/v1/gateways/me

# Revisar logs del gateway
journalctl -u echosmart-gateway | grep -i "sync\|error"
```

**Causas comunes:**

| Causa | Solución |
|-------|---------|
| Sin conexión a Internet | Verificar `ping 8.8.8.8` |
| API key expirada | Regenerar la key en el panel admin |
| URL incorrecta | Verificar `CLOUD_API_URL` en `.env` |
| Certificado TLS inválido | Verificar el certificado del servidor |

---

## 2. Backend (FastAPI)

### 2.1 Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres
# O:
sudo systemctl status postgresql

# Probar conexión
psql -h localhost -U echosmart -d echosmart -c "SELECT 1;"
```

**Causas comunes:**

| Causa | Solución |
|-------|---------|
| PostgreSQL no está corriendo | `docker-compose up -d postgres` |
| `DATABASE_URL` incorrecta | Verificar formato: `postgresql://user:pass@host:port/db` |
| Contraseña incorrecta | Verificar en `.env` y en la configuración de PostgreSQL |
| Base de datos no existe | `createdb echosmart` |

### 2.2 Error de conexión a InfluxDB

```bash
# Verificar que InfluxDB esté corriendo
curl -s http://localhost:8086/health

# Verificar token
curl -s -H "Authorization: Token $INFLUXDB_TOKEN" \
  http://localhost:8086/api/v2/buckets
```

### 2.3 Error 401 "Token expired" o "Invalid token"

| Causa | Solución |
|-------|---------|
| Access token expirado | Usar el endpoint `/api/v1/auth/refresh` con el refresh token |
| Refresh token expirado | El usuario debe iniciar sesión de nuevo |
| `JWT_SECRET_KEY` cambió | Todos los tokens existentes quedan invalidados; los usuarios deben re-autenticarse |

### 2.4 Error 429 "Rate limit exceeded"

El usuario ha superado el límite de solicitudes por minuto.

```bash
# Esperar 1 minuto y reintentar
# O aumentar el límite en la configuración del rate limiter
```

### 2.5 Migraciones fallidas

```bash
# Ver el estado actual de migraciones
alembic current

# Intentar migrar de nuevo
alembic upgrade head

# Si hay conflictos, generar una nueva migración
alembic revision --autogenerate -m "fix migration conflict"
```

---

## 3. Frontend (React)

### 3.1 Error "Network Error" al conectar con la API

| Causa | Solución |
|-------|---------|
| Backend no está corriendo | Iniciar con `uvicorn main:app --reload` |
| `VITE_API_URL` incorrecto | Verificar en `.env` que apunte al backend |
| CORS no configurado | Agregar el origen del frontend en `CORS_ORIGINS` del backend |
| Proxy no configurado | En desarrollo, verificar la configuración de Vite proxy |

### 3.2 WebSocket se desconecta

```javascript
// Verificar en la consola del navegador
// Abrir DevTools → Network → WS

// Causas comunes:
// 1. Token expirado → Refrescar token antes de reconectar
// 2. Servidor reiniciado → Implementar reconexión automática
// 3. Firewall bloqueando WS → Verificar que el puerto esté abierto
```

### 3.3 Gráficas no se actualizan en tiempo real

1. Verificar que el WebSocket esté conectado (pestaña Network en DevTools).
2. Verificar que el componente esté suscrito al sensor correcto.
3. Verificar que el backend esté emitiendo eventos.

---

## 4. Docker

### 4.1 Contenedor no inicia

```bash
# Ver logs del contenedor
docker logs echosmart-backend

# Ver estado de todos los contenedores
docker-compose ps

# Reconstruir la imagen
docker-compose build --no-cache backend
docker-compose up -d backend
```

### 4.2 Error "port already in use"

```bash
# Encontrar el proceso que ocupa el puerto
sudo ss -tlnp | grep :8000

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

### 4.3 Problemas de volúmenes y persistencia

```bash
# Listar volúmenes
docker volume ls

# Inspeccionar un volumen
docker volume inspect echosmart_pgdata

# Eliminar volúmenes (¡CUIDADO: borra datos!)
docker-compose down -v
```

---

## 5. Problemas Generales

### 5.1 Latencia alta en lecturas de sensores

| Punto de revisión | Diagnóstico | Umbral esperado |
|-------------------|-------------|-----------------|
| Lectura del sensor | Medir tiempo en `sensor_manager.py` | < 1 s por sensor |
| Caché SQLite | Verificar tamaño de BD | < 100 MB |
| Sincronización cloud | Revisar tiempo de batch | < 5 s por lote |
| API response time | Revisar logs de FastAPI | < 200 ms p99 |

### 5.2 Alto uso de memoria en Raspberry Pi

```bash
# Ver uso de memoria
free -h

# Ver procesos por memoria
ps aux --sort=-%mem | head -10

# Si el gateway consume demasiado:
# 1. Reducir número de sensores activos
# 2. Limpiar la base SQLite de lecturas ya sincronizadas
# 3. Reducir frecuencia de polling
```

### 5.3 Disco lleno

```bash
# Verificar espacio
df -h

# Encontrar archivos grandes
du -sh /var/log/* | sort -rh | head -10

# Limpiar logs antiguos
sudo journalctl --vacuum-time=7d

# Limpiar imágenes Docker no utilizadas
docker system prune -a
```

---

## 6. Comandos de Diagnóstico Rápido

```bash
# === Gateway ===
systemctl status echosmart-gateway       # Estado del servicio
journalctl -u echosmart-gateway -f       # Logs en tiempo real
i2cdetect -y 1                           # Escaneo I2C
ls /sys/bus/w1/devices/                  # Dispositivos 1-Wire
mosquitto_sub -t "echosmart/#" -v        # Monitor MQTT

# === Backend ===
curl http://localhost:8000/health        # Health check
docker-compose ps                        # Estado de contenedores
docker logs echosmart-backend --tail 50  # Últimos logs

# === Base de datos ===
psql -h localhost -U echosmart -c "\dt"  # Listar tablas
redis-cli ping                           # Verificar Redis
curl http://localhost:8086/health        # Health de InfluxDB
```

---

*Volver al [Índice de Documentación](README.md)*
