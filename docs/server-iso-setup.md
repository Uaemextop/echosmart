# EchoSmart — ISO del Servidor: Guía de Instalación y Configuración

Guía completa para instalar el servidor EchoSmart desde el ISO personalizado. El ISO incluye TODO el software necesario: un administrador solo necesita flashear, responder 5 preguntas, y el servidor queda 100% funcional.

---

## 1. Requisitos del Servidor

### Hardware Mínimo

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 2 cores x86_64 | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disco | 80 GB SSD | 200+ GB SSD |
| Red | 1 Gbps Ethernet | 1 Gbps + IP pública estática |
| SO Base | Ubuntu Server 22.04 LTS | Incluido en el ISO |

### Requisitos de Red

- IP pública estática (para acceso desde gateways remotos)
- Puertos abiertos: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8883 (MQTT TLS)
- Dominio DNS configurado apuntando a la IP del servidor (recomendado)

---

## 2. Instalación desde ISO

### 2.1 Descargar el ISO

```bash
# Descargar desde GitHub Releases
wget https://github.com/Uaemextop/echosmart/releases/latest/download/echosmart-server-amd64.iso

# Verificar integridad
sha256sum echosmart-server-amd64.iso
# Comparar con el hash publicado en la release
```

### 2.2 Crear USB Booteable

```bash
# Linux / macOS
sudo dd if=echosmart-server-amd64.iso of=/dev/sdX bs=4M status=progress

# Windows: usar Rufus (https://rufus.ie) o Balena Etcher
```

### 2.3 Instalar en el Servidor

1. Arrancar el servidor desde el USB
2. Seleccionar idioma y teclado
3. La instalación es **automática** (preseed):
   - Particionamiento automático
   - Instalación de Ubuntu Server 22.04
   - Instalación de Docker, Nginx, Certbot, UFW
   - Instalación de EchoSmart
4. El servidor reinicia automáticamente al terminar (~15 minutos)

### 2.4 Instalación en Máquina Virtual (Testing)

```bash
# VirtualBox
VBoxManage createvm --name echosmart-server --register
VBoxManage modifyvm echosmart-server --memory 4096 --cpus 2
VBoxManage createhd --filename echosmart-server.vdi --size 80000
VBoxManage storagectl echosmart-server --name "SATA" --add sata
VBoxManage storageattach echosmart-server --storagectl "SATA" --port 0 --type hdd --medium echosmart-server.vdi
VBoxManage storageattach echosmart-server --storagectl "SATA" --port 1 --type dvddrive --medium echosmart-server-amd64.iso
VBoxManage startvm echosmart-server
```

---

## 3. Configuración Inicial (Primer Login)

Al hacer login por primera vez (SSH o consola), se ejecuta automáticamente el wizard de configuración:

```
╔══════════════════════════════════════════════╗
║  🌱 EchoSmart Server Setup                  ║
║  Configuración inicial del servidor          ║
╚══════════════════════════════════════════════╝

Paso 1/6: Dominio
  Ingrese el dominio principal del servidor
  (ej: echosmart.miempresa.com): _

Paso 2/6: Email del Administrador
  Este email se usará para:
  - Certificado SSL (Let's Encrypt)
  - Cuenta de administrador
  (ej: admin@miempresa.com): _

Paso 3/6: Contraseña del Administrador
  Mínimo 12 caracteres, con mayúsculas, números y símbolos
  Contraseña: _

Paso 4/6: Configuración SMTP
  Host SMTP (ej: smtp.gmail.com): _
  Puerto (587): _
  Usuario SMTP: _
  Contraseña SMTP: _
  Email "From" (ej: noreply@echosmart.io): _

Paso 5/6: Red
  ¿Usar DHCP o IP estática?
  [1] DHCP (automático)
  [2] IP estática
  Selección: _

Paso 6/6: Zona Horaria
  (ej: America/Mexico_City): _
```

### Lo que hace el wizard automáticamente:

1. Genera credenciales aleatorias para PostgreSQL, InfluxDB, Redis, MQTT, JWT
2. Configura Nginx con el dominio proporcionado
3. Solicita certificado SSL con Let's Encrypt
4. Configura SMTP en el backend
5. Crea el usuario administrador en la base de datos
6. Inicia todos los servicios Docker
7. Verifica que todo funciona correctamente
8. Envía email de prueba al administrador

---

## 4. Administración del Servidor — `echosmart-ctl`

### Comandos Principales

```bash
# Estado de todos los servicios
echosmart-ctl status

# Iniciar / detener / reiniciar
echosmart-ctl start
echosmart-ctl stop
echosmart-ctl restart

# Ver logs (todos o de un servicio específico)
echosmart-ctl logs
echosmart-ctl logs backend
echosmart-ctl logs --follow

# Backup manual
echosmart-ctl backup
# Restaurar desde backup
echosmart-ctl restore /var/backups/echosmart/backup-2026-03-25.tar.gz

# Actualizar a la última versión
echosmart-ctl update

# Verificación de salud completa
echosmart-ctl health

# Gestión de usuarios
echosmart-ctl add-user admin@empresa.com admin
echosmart-ctl reset-password admin@empresa.com

# Renovar certificado SSL
echosmart-ctl ssl-renew

# Generar reporte de diagnóstico
echosmart-ctl diagnostics > diagnostics.txt

# Re-ejecutar wizard de configuración
echosmart-ctl config
```

### Ejemplo de Output de `echosmart-ctl status`

```
╔═══════════════════════════════════════════════════════╗
║  EchoSmart Server v1.0.0 — Estado del Sistema        ║
╠═══════════════════════════════════════════════════════╣
║  Servicio          │ Estado    │ Puerto │ Uptime      ║
║────────────────────┼───────────┼────────┼─────────────║
║  Backend (FastAPI)  │ ✅ Running │ 8000   │ 5d 12h 30m ║
║  Frontend (React)   │ ✅ Running │ 80/443 │ 5d 12h 30m ║
║  PostgreSQL         │ ✅ Running │ 5432   │ 5d 12h 30m ║
║  InfluxDB           │ ✅ Running │ 8086   │ 5d 12h 30m ║
║  Redis              │ ✅ Running │ 6379   │ 5d 12h 30m ║
║  Mosquitto (MQTT)   │ ✅ Running │ 8883   │ 5d 12h 30m ║
║  Grafana            │ ✅ Running │ 3000   │ 5d 12h 30m ║
║  Prometheus         │ ✅ Running │ 9090   │ 5d 12h 30m ║
╠═══════════════════════════════════════════════════════╣
║  CPU: 15% │ RAM: 3.2/8 GB │ Disco: 25/200 GB        ║
║  Gateways conectados: 3 │ Sensores activos: 15      ║
║  Último backup: hace 6 horas                         ║
╚═══════════════════════════════════════════════════════╝
```

---

## 5. Estructura de Archivos en el Servidor

```
/opt/echosmart/
├── docker-compose.prod.yml     # Orquestación de servicios
├── credentials.env             # Credenciales (permisos 600)
├── nginx/
│   ├── nginx.conf              # Configuración principal
│   └── sites/echosmart.conf    # Virtual host del dominio
├── ssl/
│   ├── cert.pem                # Certificado SSL
│   └── key.pem                 # Clave privada
├── data/
│   ├── postgres/               # Datos de PostgreSQL
│   ├── influxdb/               # Datos de InfluxDB
│   ├── redis/                  # Datos de Redis
│   └── mosquitto/              # Datos de Mosquitto
├── logs/
│   ├── backend/
│   ├── nginx/
│   └── gateway-sync/
└── scripts/
    ├── backup.sh
    ├── restore.sh
    └── health-check.sh

/usr/local/bin/
└── echosmart-ctl               # CLI de administración

/var/backups/echosmart/
├── backup-2026-03-25.tar.gz    # Backups diarios
└── ...
```

---

## 6. Backups Automáticos

| Componente | Frecuencia | Retención | Ubicación |
|------------|-----------|-----------|-----------|
| PostgreSQL | Diario 02:00 | 30 días | `/var/backups/echosmart/` |
| InfluxDB | Diario 03:00 | 30 días | `/var/backups/echosmart/` |
| Redis | Cada 6 horas | 7 días | `/var/backups/echosmart/` |
| Configuración | Diario 04:00 | 90 días | `/var/backups/echosmart/` |

Los backups se encriptan con GPG y opcionalmente se pueden sincronizar a un servidor remoto (S3, GCS, o SCP).

---

## 7. Seguridad

- **Firewall (UFW)**: solo puertos 22, 80, 443, 8883
- **fail2ban**: protección contra brute force SSH (ban 10 intentos en 10 min)
- **SSL/TLS**: Let's Encrypt con renovación automática
- **SSH**: solo autenticación por clave, no root login
- **Actualizaciones**: `unattended-upgrades` para patches de seguridad
- **Docker**: non-root containers, read-only filesystems
- **Credenciales**: generadas aleatoriamente, almacenadas con permisos 600

---

## 8. Actualización del Servidor

```bash
# Actualización manual
echosmart-ctl update

# El proceso:
# 1. Descarga nuevas imágenes Docker
# 2. Ejecuta migraciones de base de datos
# 3. Reinicia servicios con zero-downtime
# 4. Verifica health checks
# 5. Rollback automático si algo falla
```

---

## 9. Monitoreo

Acceder a Grafana en `https://dominio/grafana/` con credenciales de admin.

### Dashboards Incluidos

1. **System Overview**: CPU, RAM, disco, red
2. **API Performance**: latencia, throughput, errores
3. **Sensor Data**: lecturas por minuto, valores actuales
4. **Gateway Status**: online/offline, sync lag
5. **Alerts**: alertas activas, historial

---

*Volver al [Índice de Documentación](README.md)*
