# EchoSmart - Documentación de Backend (FastAPI)

## 1. Estructura de Funciones Clave por Módulo

### 1.1 Auth Service (`src/services/auth_service.py`)

```python
"""
Servicio de autenticación y gestión de JWT tokens

Responsabilidades:
  • Validación de credenciales (email/password)
  • Generación de JWT access/refresh tokens
  • Validación y revocación de tokens
  • Integración con HashiCorp Vault (opcional)
"""

class AuthService:
    
    @staticmethod
    async def login(
        email: str,
        password: str,
        db: Session
    ) -> TokenResponse:
        """
        Autentica un usuario y genera tokens JWT
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            db: Sesión de base de datos
            
        Returns:
            TokenResponse: {access_token, refresh_token, token_type, expires_in}
            
        Raises:
            InvalidCredentialsException: Si email/password incorrectos
            UserNotActivedException: Si usuario inactivo
            
        Process:
            1. Query usuario por email
            2. Validar password con bcrypt.verify()
            3. Cargar permisos desde tabla user_permissions
            4. Generar JWT con claims: sub, tenant_id, role, exp
            5. Guardar refresh token en Redis con TTL 30 días
            6. Retornar tokens
            
        JWT Payload:
            {
                "sub": "user-123",
                "email": "user@company.com",
                "tenant_id": "tenant-abc",
                "role": "admin",
                "permissions": ["read:sensors", "write:alerts"],
                "exp": 1678987634,
                "iat": 1678901234,
                "iss": "echosmart.com"
            }
        """
        pass
    
    @staticmethod
    async def refresh_token(
        refresh_token: str,
        db: Session
    ) -> TokenResponse:
        """
        Genera nuevo access token usando refresh token
        
        Args:
            refresh_token: Token de refresco (del cookie)
            db: Sesión de base de datos
            
        Returns:
            TokenResponse: Nuevo access_token + refresh_token
            
        Raises:
            InvalidTokenException: Si token inválido/expirado
            
        Process:
            1. Validar signature del refresh token
            2. Verificar que NO está en blacklist
            3. Extraer user_id y tenant_id del token
            4. Verificar que usuario aún existe y está activo
            5. Generar nuevo access token (24h)
            6. Generar nuevo refresh token (30d)
            7. Guardar nuevo refresh en Redis
            8. Añadir viejo refresh a blacklist (TTL 30d)
        """
        pass
    
    @staticmethod
    async def logout(
        refresh_token: str,
        user_id: str
    ) -> None:
        """
        Invalida todos los tokens del usuario
        
        Process:
            1. Obtener todos los refresh tokens del usuario desde Redis
            2. Añadir todos a blacklist con TTL 30 días
            3. Log de logout en audit table
        """
        pass
    
    @staticmethod
    def verify_token(token: str) -> Dict:
        """
        Valida JWT token y extrae claims
        
        Validaciones:
            ✓ Signature correcta (secret key)
            ✓ No expirado (exp > now)
            ✓ No revocado (no en blacklist Redis)
            ✓ iss == "echosmart.com"
            
        Returns:
            {"sub": user_id, "tenant_id": tenant_id, "role": role, ...}
        """
        pass
```

---

### 1.2 Sensor Service (`src/services/sensor_service.py`)

```python
"""
Lógica de negocio para gestión de sensores

Responsabilidades:
  • CRUD de sensores
  • Auto-discovery y registro
  • Validación de sensores
  • Caché de configuración
"""

class SensorService:
    
    @staticmethod
    async def create_sensor(
        sensor_data: SensorCreate,
        tenant_id: str,
        db: Session
    ) -> SensorResponse:
        """
        Crea un nuevo sensor en la plataforma
        
        Args:
            sensor_data: {name, type, gateway_id, location}
            tenant_id: ID del tenant (desde JWT)
            db: Sesión BD
            
        Returns:
            SensorResponse: Sensor creado con sensor_id
            
        Validaciones:
            ✓ Tenant puede crear más sensores (check max_sensors en plan)
            ✓ Gateway pertenece al mismo tenant
            ✓ Type es válido (temperature, humidity, etc)
            ✓ No existe sensor con mismo sensor_uuid
            
        Side Effects:
            • Invalidar caché de sensores del tenant
            • Enviar comando MQTT al gateway para activar sensor
            • Log en audit table
        """
        pass
    
    @staticmethod
    async def discover_sensors(
        gateway_id: str,
        tenant_id: str,
        db: Session
    ) -> List[SensorResponse]:
        """
        Descubre sensores auto-conectados (SSDP)
        
        Process:
            1. Gateway envía lista de sensores detectados
            2. Validar que gateway pertenece al tenant
            3. Para cada sensor detectado:
               a. Buscar en DB por sensor_uuid
               b. Si existe: actualizar last_seen, status=online
               c. Si no existe: crear nuevo con status=pending_activation
            4. Retornar sensores nuevos
            
        Usado por: POST /api/v1/sensors/discover (desde Gateway)
        """
        pass
    
    @staticmethod
    async def get_sensor_by_id(
        sensor_id: str,
        tenant_id: str,
        db: Session
    ) -> SensorResponse:
        """
        Obtiene detalles de un sensor con RLS
        
        Query:
            SELECT * FROM sensors
            WHERE sensor_id = ? AND tenant_id = ?
            
        Includes:
            • Última lectura
            • Estado online/offline
            • Configuración de alertas
        """
        pass
    
    @staticmethod
    async def list_sensors(
        tenant_id: str,
        gateway_id: Optional[str],
        sensor_type: Optional[str],
        limit: int = 100,
        offset: int = 0,
        db: Session = None
    ) -> PaginatedResponse:
        """
        Lista sensores del tenant con filtros
        
        Filters:
            • gateway_id: Filtrar por gateway específico
            • sensor_type: Filtrar por tipo (temperature, etc)
            
        Query:
            SELECT s.*, 
                   (SELECT value FROM sensor_readings 
                    WHERE sensor_id=s.sensor_id 
                    ORDER BY time DESC LIMIT 1) as last_reading
            FROM sensors s
            WHERE s.tenant_id = ? 
              AND (gateway_id = ? OR ? IS NULL)
              AND (type = ? OR ? IS NULL)
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
            
        Performance:
            • Usar índices: (tenant_id, gateway_id, type, created_at)
            • Cachear resultado por 5 minutos en Redis
            • Invalidar caché cuando sensor cambia
        """
        pass
    
    @staticmethod
    async def update_sensor_config(
        sensor_id: str,
        config: SensorConfigUpdate,
        tenant_id: str,
        db: Session
    ) -> SensorResponse:
        """
        Actualiza configuración del sensor
        
        Campos actualizables:
            • name
            • location
            • calibration_offset (para ajustes manuales)
            • enabled (desactivar temporalmente)
            
        Side Effects:
            • MQTT publish a sensors/{sensor_uuid}/config
            • Invalidar caché sensor
            • Log en audit
        """
        pass
    
    @staticmethod
    async def delete_sensor(
        sensor_id: str,
        tenant_id: str,
        db: Session
    ) -> None:
        """
        Elimina un sensor (soft delete)
        
        Process:
            1. Validar que sensor pertenece al tenant
            2. Soft delete: enabled = FALSE (no borrar datos históricos)
            3. Eliminar alert configs asociadas
            4. MQTT publish a sensors/{sensor_uuid}/status {online: false}
            5. Log en audit
        """
        pass
```

---

### 1.3 Reading Service (`src/services/reading_service.py`)

```python
"""
Gestión de lecturas de sensores y análisis

Responsabilidades:
  • Almacenamiento en TimescaleDB
  • Agregaciones (1h, 1d, 1m)
  • Estadísticas (min, max, avg)
  • Queries de histórico
"""

class ReadingService:
    
    @staticmethod
    async def store_readings_batch(
        readings: List[ReadingCreate],
        tenant_id: str,
        db: Session,
        timescale_db: Connection
    ) -> BatchResponse:
        """
        Almacena lote de lecturas desde el gateway
        
        Args:
            readings: [{sensor_id, value, timestamp, unit}]
            tenant_id: Del JWT (validado en middleware)
            
        Process:
            1. Validar que todas las lecturas pertenecen al tenant
            2. Validar rango de valores (sensor_type-specific)
            3. Insert en TimescaleDB en bulk (batch INSERT)
            4. Update last_reading en tabla sensors
            5. Enqueue alert evaluation en RabbitMQ
            6. Actualizar caché Redis (last_reading)
            
        Performance:
            • Usar COPY (PostgreSQL COPY command) para >100 rows
            • Async insert (no bloquea response)
            • Retornar 202 Accepted inmediatamente
            
        SQL:
            INSERT INTO sensor_readings (time, sensor_id, tenant_id, value, unit)
            SELECT * FROM UNNEST (
                ARRAY[ts1, ts2, ...],
                ARRAY[sid1, sid2, ...],
                ARRAY[v1, v2, ...],
                ARRAY[u1, u2, ...]
            ) AS t(time, sensor_id, value, unit)
        """
        pass
    
    @staticmethod
    async def get_readings_timeseries(
        sensor_id: str,
        tenant_id: str,
        date_from: datetime,
        date_to: datetime,
        interval_seconds: int = 60,
        aggregate_func: str = "avg",
        db: Session = None
    ) -> TimeSeriesResponse:
        """
        Obtiene serie temporal de lecturas con agregación
        
        Args:
            sensor_id: Sensor a consultar
            date_from, date_to: Rango de fechas
            interval_seconds: 60 (1min), 300 (5min), 3600 (1h), 86400 (1d)
            aggregate_func: "avg", "min", "max", "sum"
            
        Query:
            SELECT time_bucket(?, time) AS bucket,
                   {aggregate_func}(value) as value,
                   COUNT(*) as count,
                   MIN(value) as min,
                   MAX(value) as max
            FROM sensor_readings
            WHERE sensor_id = ?
              AND tenant_id = ?
              AND time >= ? AND time < ?
            GROUP BY bucket
            ORDER BY bucket
            
        Performance Optimization:
            • Si interval >= 3600s: usar continuous aggregate (pre-computed)
            • Si fecha range > 30 días: usar aggregated data, no raw
            • Cachear resultado por 10 minutos
            
        Returns:
            {
                sensor_id,
                data: [
                    {timestamp, value, min, max, count},
                    ...
                ]
            }
        """
        pass
    
    @staticmethod
    async def get_reading_statistics(
        sensor_id: str,
        tenant_id: str,
        date_from: datetime,
        date_to: datetime,
        db: Session = None
    ) -> StatisticsResponse:
        """
        Calcula estadísticas de una serie temporal
        
        Returns:
            {
                min: 22.1,
                max: 28.5,
                avg: 25.3,
                median: 25.4,
                stddev: 1.2,
                p95: 27.8,
                p99: 28.3,
                count: 1440
            }
            
        SQL:
            SELECT
                MIN(value) as min,
                MAX(value) as max,
                AVG(value) as avg,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) as p95,
                STDDEV(value) as stddev,
                COUNT(*) as count
            FROM sensor_readings
            WHERE sensor_id = ? AND tenant_id = ? AND time >= ? AND time < ?
        """
        pass
    
    @staticmethod
    async def compare_sensors(
        sensor_ids: List[str],
        tenant_id: str,
        date_from: datetime,
        date_to: datetime,
        db: Session = None
    ) -> ComparativeResponse:
        """
        Compara múltiples sensores en el mismo período
        
        Util para:
            • Comparar temperatura en diferentes zonas
            • Detectar desviaciones entre sensores gemelos
            
        Returns:
            {
                sensors: [
                    {
                        sensor_id,
                        name,
                        stats: {min, max, avg}
                    }
                ]
            }
        """
        pass
```

---

### 1.4 Alert Service (`src/services/alert_service.py`)

```python
"""
Motor de evaluación de alertas

Responsabilidades:
  • Evaluación de condiciones
  • Aplicación de histéresis
  • Gestión de estado (NORMAL → ALERT → CRITICAL)
  • Generación de notificaciones
"""

class AlertService:
    
    @staticmethod
    async def evaluate_alerts(
        sensor_id: str,
        current_value: float,
        timestamp: datetime,
        tenant_id: str,
        db: Session
    ) -> List[AlertTrigger]:
        """
        Evalúa todas las alertas configuradas para un sensor
        
        Process:
            1. Cargar todas las alert_configs para sensor_id
            2. Obtener histórico (últimos 15 minutos)
            3. Para cada config:
               a. Evaluar condición (gt, lt, between, etc)
               b. Aplicar duración (cuánto tiempo persistió)
               c. Aplicar histéresis (evitar flapping)
               d. Cambiar estado si es necesario
               e. Si cambio de estado → crear AlertTrigger
            4. Enqueue notifications para los triggers nuevos
            
        State Machine:
            NORMAL
              ↓ (condition met for duration)
            ALERT (severity = "high")
              ↓ (persists > 15 min)
            CRITICAL (severity = "critical")
              ↓ (condition clears for 5 min)
            NORMAL
        """
        pass
    
    @staticmethod
    async def create_alert_config(
        config_data: AlertConfigCreate,
        sensor_id: str,
        tenant_id: str,
        db: Session
    ) -> AlertConfigResponse:
        """
        Crea una nueva configuración de alerta
        
        Args:
            config_data: {
                name: "Temperatura Alta",
                condition: "gt",
                threshold_value: 30.0,
                threshold_duration_minutes: 5,
                hysteresis: 2.0,
                notification_channels: ["email", "whatsapp", "push"]
            }
            
        Validaciones:
            ✓ Sensor pertenece al tenant
            ✓ Condition es válido (gt, lt, between, eq)
            ✓ Hysteresis > 0
            ✓ Duration > 0
            
        Side Effects:
            • Invalidar caché de alert configs del sensor
            • Log en audit
        """
        pass
    
    @staticmethod
    async def acknowledge_alert(
        alert_trigger_id: str,
        user_id: str,
        tenant_id: str,
        notes: str = "",
        db: Session = None
    ) -> AlertTriggerResponse:
        """
        Marca una alerta como reconocida por el usuario
        
        Updates:
            • acknowledged = TRUE
            • acknowledged_by = user_id
            • acknowledged_at = NOW()
            • notes (opcional)
            
        Side Effects:
            • Enviar notificación "Alert acknowledged"
            • Log en audit
        """
        pass
    
    @staticmethod
    async def get_active_alerts(
        tenant_id: str,
        sensor_id: Optional[str] = None,
        limit: int = 100,
        db: Session = None
    ) -> List[AlertTriggerResponse]:
        """
        Lista alertas activas (no reconocidas) del tenant
        
        Query:
            SELECT at.*, s.name as sensor_name, ac.condition
            FROM alert_triggers at
            JOIN sensors s ON at.sensor_id = s.sensor_id
            JOIN alert_configs ac ON at.alert_config_id = ac.alert_config_id
            WHERE at.tenant_id = ?
              AND at.acknowledged = FALSE
              AND (s.sensor_id = ? OR ? IS NULL)
            ORDER BY at.triggered_at DESC
            LIMIT ?
        """
        pass
```

---

### 1.5 Report Service (`src/services/report_service.py`)

```python
"""
Generación de reportes PDF y Excel

Responsabilidades:
  • Generar PDF con gráficas
  • Generar Excel con datos crudos
  • Personalización por tenant (logo, colores)
  • Almacenamiento en S3
"""

class ReportService:
    
    @staticmethod
    async def generate_report_async(
        report_config: ReportGenerateRequest,
        tenant_id: str,
        user_id: str,
        db: Session,
        queue: RabbitMQ
    ) -> ReportJobResponse:
        """
        Enqueue un trabajo de generación de reporte
        
        Args:
            report_config: {
                report_type: "pdf" | "excel" | "csv",
                sensors: [sensor_id1, sensor_id2, ...],
                date_from: "2024-03-01",
                date_to: "2024-03-31",
                include_charts: true,
                include_statistics: true,
                include_alerts: true
            }
            
        Process:
            1. Validar que sensores pertenecen al tenant
            2. Crear record en tabla reports con status="queued"
            3. Enqueue job en RabbitMQ con report_id
            4. Retornar 202 Accepted con report_id + estimated_time
            
        Returns:
            {
                report_id: "rpt-abc123",
                status: "queued",
                estimated_time_seconds: 60,
                created_at: timestamp
            }
        """
        pass
    
    @staticmethod
    async def generate_pdf_report(
        report_id: str,
        report_config: ReportGenerateRequest,
        tenant_id: str,
        db: Session
    ) -> str:
        """
        Worker function: Genera PDF físicamente
        
        Process:
            1. Cargar datos del reporte desde BD
            2. Generar gráficas PNG (matplotlib)
            3. Cargar template HTML (Jinja2)
            4. Inyectar datos: tenant branding, gráficas, tablas
            5. Convertir HTML → PDF (WeasyPrint)
            6. Upload a S3 bucket
            7. Update report record: status=completed, s3_path=...
            8. Enviar email al usuario con link de descarga
            
        Template Variables:
            - tenant.logo_url
            - tenant.primary_color
            - tenant.company_name
            - report.title
            - sensors[].name
            - charts[].image_base64
            - statistics[]
            - alerts[]
            
        Returns:
            s3_url: "https://s3.aws.com/echosmart-reports/rpt-abc123.pdf"
        """
        pass
    
    @staticmethod
    async def generate_excel_report(
        report_id: str,
        report_config: ReportGenerateRequest,
        tenant_id: str,
        db: Session
    ) -> str:
        """
        Worker function: Genera Excel con datos
        
        Sheets:
            1. "Summary": Resumen estadístico
            2. "{Sensor Name}": Datos crudos por sensor
            3. "Alerts": Log de alertas en período
            4. "Statistics": Análisis estadístico
            
        Features:
            • Formatting: Headers en negrita, alternating row colors
            • Formulas: SUM, AVERAGE, MIN, MAX auto-insertadas
            • Charts: Gráficas integradas en Excel
            • Filtros: Auto-filter en headers
            
        Returns:
            s3_url
        """
        pass
    
    @staticmethod
    async def get_report_status(
        report_id: str,
        tenant_id: str,
        db: Session
    ) -> ReportStatusResponse:
        """
        Consulta estado de un reporte
        
        Returns:
            {
                report_id,
                status: "queued" | "generating" | "completed" | "failed",
                created_at,
                completed_at,
                download_url: "https://..." (si completado),
                expires_at: timestamp (7 días desde completado)
            }
        """
        pass
    
    @staticmethod
    async def download_report(
        report_id: str,
        tenant_id: str,
        db: Session
    ) -> FileResponse:
        """
        Descarga reporte generado (con presigned S3 URL)
        
        Validaciones:
            ✓ Reporte completado (status = completed)
            ✓ Reporte no expirado (expires_at > now)
            ✓ Usuario tiene acceso (tenant_id match)
            
        Returns:
            FileResponse con stream del archivo desde S3
        """
        pass
```

---

## 2. Endpoints REST API Specification

### 2.1 Authentication Endpoints

```
POST /api/v1/auth/login
├─ Headers: Content-Type: application/json
├─ Request: {email, password}
├─ Response 200: {access_token, refresh_token, token_type, expires_in}
├─ Response 401: {detail: "Invalid credentials"}
└─ Response 429: Too many attempts

POST /api/v1/auth/refresh
├─ Headers: Cookie: refresh_token=...
├─ Response 200: {access_token, refresh_token, expires_in}
└─ Response 401: {detail: "Refresh token expired"}

POST /api/v1/auth/logout
├─ Headers: Authorization: Bearer {token}
├─ Response 204: No content
└─ Side Effects: Todos los tokens del usuario invalidados

POST /api/v1/auth/password-reset
├─ Request: {email}
├─ Response 200: {message: "Email sent"}
└─ Process: Generar token reset, enviar email con link

POST /api/v1/auth/password-reset-confirm
├─ Request: {token, new_password}
├─ Response 200: {message: "Password updated"}
└─ Validaciones: Token válido, password fuerte (8+ chars, 1 uppercase, 1 digit)
```

### 2.2 Sensor Endpoints

```
GET /api/v1/sensors
├─ Query Params: 
│  - gateway_id (optional)
│  - type (optional): temperature, humidity, light, co2, moisture
│  - limit (default 100)
│  - offset (default 0)
├─ Headers: Authorization: Bearer {token}
├─ Response 200:
│  {
│    data: [
│      {
│        sensor_id, name, type, location,
│        last_reading: {value, unit, timestamp},
│        is_online, created_at
│      }
│    ],
│    total: 42,
│    limit: 100,
│    offset: 0
│  }
└─ RLS: Solo sensores del tenant del usuario

GET /api/v1/sensors/{sensor_id}
├─ Response 200: {sensor_id, name, type, location, last_reading, alerts_config}
└─ Response 404: If not found or access denied

POST /api/v1/sensors
├─ Request:
│  {
│    name: "Sensor Temperatura Zona A",
│    type: "temperature",
│    gateway_id: "gw-001",
│    location: "Rack 1"
│  }
├─ Response 201: {sensor_id, created_at}
├─ Validaciones:
│  ✓ Tenant puede crear más sensores (check plan limits)
│  ✓ Gateway pertenece al mismo tenant
└─ Side Effects: Invalidar caché, MQTT publish al gateway

PUT /api/v1/sensors/{sensor_id}
├─ Request: {name, location, calibration_offset, enabled}
├─ Response 200: {sensor_id, updated_at}
└─ Side Effects: MQTT publish config update

DELETE /api/v1/sensors/{sensor_id}
├─ Response 204: No content
└─ Process: Soft delete (enabled = false)

POST /api/v1/sensors/discover
├─ Headers: Authorization: Bearer {gateway_api_key}
├─ Request: {gateway_id, discovered_sensors: [{uuid, type, name}]}
├─ Response 200: {new_sensors_count, sensors: [...]}
└─ Process: Auto-discovery desde Gateway
```

### 2.3 Reading Endpoints

```
POST /api/v1/readings/batch
├─ Headers: Authorization: Bearer {gateway_api_key}
├─ Request (max 1000 readings):
│  {
│    readings: [
│      {sensor_id, value, timestamp, unit},
│      ...
│    ]
│  }
├─ Response 202: {batch_id, status: "queued", count: 123}
├─ Validations: RLS check, range validation
└─ Side Effects: Async store en TimescaleDB, enqueue alerts

GET /api/v1/readings/{sensor_id}
├─ Query Params:
│  - from: Unix timestamp (required)
│  - to: Unix timestamp (required)
│  - interval: 60|300|900|3600|86400 (default 300)
│  - aggregate: avg|min|max|sum (default avg)
├─ Response 200:
│  {
│    sensor_id,
│    data: [
│      {timestamp, value, min, max, count},
│      ...
│    ]
│  }
└─ Caching: 10 minutos en Redis

GET /api/v1/readings/{sensor_id}/statistics
├─ Query Params: from, to
├─ Response 200:
│  {
│    min: 22.1,
│    max: 28.5,
│    avg: 25.3,
│    median: 25.4,
│    stddev: 1.2,
│    p95: 27.8
│  }
└─ Uses TimescaleDB aggregates
```

### 2.4 Alert Endpoints

```
POST /api/v1/alerts/configure
├─ Request:
│  {
│    sensor_id,
│    name: "Temperatura Alta",
│    condition: "gt",
│    threshold_value: 30.0,
│    threshold_duration_minutes: 5,
│    hysteresis: 2.0,
│    notification_channels: ["email", "whatsapp", "push"]
│  }
├─ Response 201: {alert_config_id, created_at}
└─ Side Effects: Invalidar caché

GET /api/v1/alerts/active
├─ Response 200:
│  {
│    data: [
│      {
│        alert_trigger_id,
│        sensor_id, sensor_name,
│        triggered_value, threshold,
│        severity: "high|critical",
│        triggered_at,
│        acknowledged: false
│      }
│    ]
│  }
└─ RLS: Solo alertas del tenant

PUT /api/v1/alerts/{alert_trigger_id}/acknowledge
├─ Request: {notes: "Ventilador activado"}
├─ Response 200: {acknowledged_at, acknowledged_by}
└─ Side Effects: Notificación a admin

GET /api/v1/alerts/history
├─ Query Params: from, to, limit, offset
├─ Response 200: Historial de alertas disparadas
└─ Filtrable por sensor_id, severity
```

### 2.5 Report Endpoints

```
POST /api/v1/reports/generate
├─ Request:
│  {
│    report_type: "pdf|excel|csv",
│    sensors: ["sensor-1", "sensor-2"],
│    date_from: "2024-03-01T00:00:00Z",
│    date_to: "2024-03-31T23:59:59Z",
│    include_charts: true,
│    include_statistics: true
│  }
├─ Response 202: {report_id, status: "queued", estimated_time: 60}
└─ Async job, no bloquea

GET /api/v1/reports/{report_id}
├─ Response 200 (completing):
│  {
│    report_id,
│    status: "completed",
│    download_url: "https://...",
│    expires_at: timestamp
│  }
├─ Response 202 (still generating): {status: "generating"}
└─ Response 404 (failed): {status: "failed", error: "..."}

GET /api/v1/reports/{report_id}/download
├─ Response 200: FileResponse (stream PDF/Excel)
├─ Validations: Reporte completado, no expirado, acceso autenticado
└─ Headers: Content-Disposition: attachment; filename="report.pdf"

GET /api/v1/reports/history
├─ Query Params: limit, offset
├─ Response 200: Lista de reportes generados
└─ Incluye: created_at, report_type, expires_at
```

