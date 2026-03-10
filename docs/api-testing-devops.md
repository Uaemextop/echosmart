# EchoSmart - Guía Completa de API y Testing

## 1. Especificación Completa de API REST

### 1.1 Autenticación y Autorización

#### JWT Token Structure
```python
# Payload JWT
{
  "sub": "user-uuid",           # Subject (user ID)
  "email": "user@example.com",
  "tenant_id": "tenant-uuid",
  "role": "operator",           # admin, operator, viewer
  "iat": 1678901200,           # Issued at
  "exp": 1678987600,           # Expires in 24 hours
  "scope": ["sensors:read", "sensors:write", "alerts:read"]
}
```

#### Endpoints de Autenticación

```
POST /api/v1/auth/login
Description: Autenticación de usuario

Request:
{
  "email": "operator@company.com",
  "password": "SecurePassword123!",
  "remember_me": true
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "operator@company.com",
    "full_name": "John Operator",
    "role": "operator",
    "tenant_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "is_active": true
  }
}

Error (401 Unauthorized):
{
  "error": "invalid_credentials",
  "message": "Email or password is incorrect"
}
```

```
POST /api/v1/auth/refresh
Description: Refrescar token de acceso

Headers:
Authorization: Bearer {refresh_token}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

```
POST /api/v1/auth/logout
Description: Logout del usuario

Headers:
Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "Successfully logged out"
}
```

```
POST /api/v1/auth/forgot-password
Description: Solicitar reset de contraseña

Request:
{
  "email": "user@example.com"
}

Response (200 OK):
{
  "message": "Reset email sent if account exists"
}
```

```
POST /api/v1/auth/reset-password
Description: Resetear contraseña con token

Request:
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePassword456!",
  "confirm_password": "NewSecurePassword456!"
}

Response (200 OK):
{
  "message": "Password reset successfully"
}
```

---

### 1.2 Gateways API

```
GET /api/v1/gateways
Description: Listar todos los gateways del tenant

Query Parameters:
  - page: integer (default: 1)
  - limit: integer (default: 20, max: 100)
  - search: string (buscar por nombre o gateway_id)
  - status: string (online, offline)

Headers:
Authorization: Bearer {access_token}

Response (200 OK):
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "gateway_id": "echosmart-gw-001",
      "name": "Invernadero A",
      "location": "Valle de Bravo, México",
      "online_status": true,
      "last_heartbeat": "2024-03-09T15:45:30Z",
      "ip_address": "192.168.1.100",
      "software_version": "1.2.0",
      "config_version": "v2.1.0",
      "sensor_count": 5,
      "error_count": 0,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-03-09T15:45:30Z"
    }
  ],
  "pagination": {
    "total": 3,
    "page": 1,
    "limit": 20,
    "pages": 1
  }
}

Error (401 Unauthorized):
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

```
POST /api/v1/gateways
Description: Registrar nuevo gateway

Request:
{
  "gateway_id": "echosmart-gw-002",
  "name": "Invernadero B",
  "location": "Querétaro, México"
}

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "gateway_id": "echosmart-gw-002",
  "api_key": "sk-gateway-abc123def456...",  # Guardar seguro
  "name": "Invernadero B",
  "location": "Querétaro, México",
  "created_at": "2024-03-09T16:00:00Z"
}
```

```
GET /api/v1/gateways/{gateway_id}
Description: Obtener detalles de un gateway

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "gateway_id": "echosmart-gw-001",
  "name": "Invernadero A",
  "location": "Valle de Bravo, México",
  "online_status": true,
  "last_heartbeat": "2024-03-09T15:45:30Z",
  "sensors": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "sensor_id": "temp-interior",
      "name": "Temperatura Interior",
      "type": "ds18b20",
      "unit": "°C",
      "last_reading": 25.3,
      "is_online": true
    }
  ],
  "status_details": {
    "memory_usage_percent": 45,
    "disk_usage_percent": 32,
    "uptime_seconds": 604800,
    "cpu_temp_celsius": 52.3
  }
}
```

```
PUT /api/v1/gateways/{gateway_id}
Description: Actualizar configuración del gateway

Request:
{
  "name": "Invernadero A - Sector Principal",
  "location": "Valle de Bravo, México - Updated"
}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "gateway_id": "echosmart-gw-001",
  "name": "Invernadero A - Sector Principal",
  "location": "Valle de Bravo, México - Updated",
  "updated_at": "2024-03-09T16:05:00Z"
}
```

```
POST /api/v1/gateways/{gateway_id}/reboot
Description: Reiniciar gateway

Response (202 Accepted):
{
  "message": "Gateway reboot scheduled",
  "estimated_time": 120  # segundos
}
```

```
DELETE /api/v1/gateways/{gateway_id}
Description: Eliminar gateway (marca como no activo)

Response (204 No Content)
```

---

### 1.3 Sensores API

```
GET /api/v1/sensors
Description: Listar sensores

Query Parameters:
  - gateway_id: string (filtrar por gateway)
  - type: string (ds18b20, dht22, bh1750, soil_moisture, mhz19c)
  - status: string (online, offline, error)
  - search: string (buscar por nombre)
  - page: integer
  - limit: integer (default: 50)

Response (200 OK):
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "gateway_id": "550e8400-e29b-41d4-a716-446655440000",
      "sensor_id": "temp-interior",
      "name": "Temperatura Interior",
      "type": "ds18b20",
      "unit": "°C",
      "location": "Centro del invernadero",
      "last_reading": {
        "value": 25.3,
        "timestamp": "2024-03-09T15:45:30Z",
        "is_valid": true
      },
      "is_online": true,
      "error_count": 0,
      "polling_interval_seconds": 60,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-03-09T15:45:30Z"
    }
  ],
  "pagination": {...}
}
```

```
POST /api/v1/sensors
Description: Registrar nuevo sensor

Request:
{
  "gateway_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Temperatura Interior",
  "type": "ds18b20",
  "device_id": "28-0516a42651ff",
  "unit": "°C",
  "location": "Centro del invernadero",
  "polling_interval_seconds": 60,
  "retention_days": 30
}

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "gateway_id": "550e8400-e29b-41d4-a716-446655440000",
  "sensor_id": "temp-interior",  # auto-generado
  "name": "Temperatura Interior",
  "type": "ds18b20",
  "device_id": "28-0516a42651ff",
  "unit": "°C",
  "created_at": "2024-03-09T16:10:00Z"
}
```

```
GET /api/v1/sensors/{sensor_id}/readings
Description: Obtener lecturas históricas de un sensor

Query Parameters:
  - from: ISO8601 timestamp (required)
  - to: ISO8601 timestamp (required)
  - interval: integer (segundos entre puntos agregados, optional)
  - aggregation: string (mean, min, max, sum - default: mean)
  - limit: integer (max: 10000)

Example:
GET /api/v1/sensors/550e8400-e29b-41d4-a716-446655440100/readings?
  from=2024-03-01T00:00:00Z&
  to=2024-03-09T23:59:59Z&
  interval=3600&
  aggregation=mean

Response (200 OK):
{
  "sensor_id": "550e8400-e29b-41d4-a716-446655440100",
  "sensor_name": "Temperatura Interior",
  "unit": "°C",
  "readings": [
    {
      "timestamp": "2024-03-01T00:00:00Z",
      "value": 24.5,
      "count": 60  # número de puntos agregados
    },
    {
      "timestamp": "2024-03-01T01:00:00Z",
      "value": 24.8,
      "count": 60
    }
  ],
  "statistics": {
    "min": 18.2,
    "max": 32.1,
    "mean": 25.3,
    "std_dev": 3.2,
    "total_points": 216
  }
}
```

```
PUT /api/v1/sensors/{sensor_id}
Description: Actualizar configuración del sensor

Request:
{
  "name": "Temperatura Interior - Actualizado",
  "location": "Centro - Sector A",
  "polling_interval_seconds": 120,
  "enabled": true
}

Response (200 OK):
{...sensor_data...}
```

```
DELETE /api/v1/sensors/{sensor_id}
Description: Eliminar sensor

Response (204 No Content)
```

---

### 1.4 Alertas API

```
GET /api/v1/alerts
Description: Listar alertas

Query Parameters:
  - severity: string (critical, high, medium, low)
  - status: string (new, acknowledged, resolved)
  - sensor_id: string (filtrar por sensor)
  - from_date: ISO8601 timestamp
  - to_date: ISO8601 timestamp
  - limit: integer (default: 100)

Response (200 OK):
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440200",
      "rule_id": "550e8400-e29b-41d4-a716-446655440201",
      "sensor_id": "550e8400-e29b-41d4-a716-446655440100",
      "sensor_name": "Temperatura Interior",
      "value": 36.5,
      "severity": "critical",
      "status": "new",
      "message": "Temperatura muy alta (>35°C)",
      "triggered_at": "2024-03-09T16:15:00Z",
      "acknowledged_at": null,
      "resolved_at": null
    }
  ],
  "total_count": 42,
  "unacknowledged_count": 5
}
```

```
POST /api/v1/alerts/{alert_id}/acknowledge
Description: Reconocer una alerta

Request:
{
  "notes": "Ya verificado y en reparación"
}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440200",
  "status": "acknowledged",
  "acknowledged_at": "2024-03-09T16:20:00Z",
  "acknowledged_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

```
POST /api/v1/alerts/{alert_id}/resolve
Description: Marcar alerta como resuelta

Request:
{
  "notes": "Problema solucionado"
}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440200",
  "status": "resolved",
  "resolved_at": "2024-03-09T16:25:00Z"
}
```

```
GET /api/v1/alert-rules
Description: Listar reglas de alertas

Response (200 OK):
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440201",
      "sensor_id": "550e8400-e29b-41d4-a716-446655440100",
      "sensor_name": "Temperatura Interior",
      "name": "Temperatura Crítica",
      "description": "Alertar si temperatura supera 35°C",
      "condition": "gt",
      "threshold_value": 35,
      "severity": "critical",
      "enabled": true,
      "cooldown_minutes": 30,
      "action": "email",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

```
POST /api/v1/alert-rules
Description: Crear nueva regla de alerta

Request:
{
  "sensor_id": "550e8400-e29b-41d4-a716-446655440100",
  "name": "Humedad Baja",
  "condition": "lt",
  "threshold_value": 20,
  "severity": "warning",
  "cooldown_minutes": 60,
  "action": "email",
  "enabled": true
}

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440202",
  "sensor_id": "550e8400-e29b-41d4-a716-446655440100",
  ...
}
```

---

## 2. Testing Comprehensive

### 2.1 Unit Tests (Backend - pytest)

```python
# tests/test_sensor_manager.py

import pytest
from datetime import datetime
from gateway.src.sensor_manager import SensorManager, SensorReading

@pytest.fixture
def sensor_manager():
    """Fixture para instancia de SensorManager"""
    return SensorManager(config_path='tests/fixtures/sensors_test.json')

class TestSensorManager:
    """Test suite para SensorManager"""
    
    def test_initialize_sensors(self, sensor_manager):
        """Verificar inicialización de sensores"""
        assert len(sensor_manager.sensors) > 0
        assert 'temp-interior' in sensor_manager.sensors
    
    def test_read_sensor_success(self, sensor_manager, monkeypatch):
        """Test lectura exitosa de sensor"""
        def mock_read():
            return 25.3
        
        monkeypatch.setattr(
            sensor_manager.sensors['temp-interior'],
            'read',
            mock_read
        )
        
        reading = sensor_manager.read_sensor('temp-interior')
        
        assert reading.is_valid is True
        assert reading.value == 25.3
        assert reading.sensor_id == 'temp-interior'
    
    def test_read_sensor_not_found(self, sensor_manager):
        """Test lectura de sensor inexistente"""
        reading = sensor_manager.read_sensor('nonexistent-sensor')
        
        assert reading.is_valid is False
        assert reading.error_message == "Sensor no encontrado"
    
    def test_read_all_sensors(self, sensor_manager, monkeypatch):
        """Test lectura de todos los sensores"""
        def mock_read():
            return 25.0
        
        for sensor in sensor_manager.sensors.values():
            monkeypatch.setattr(sensor, 'read', mock_read)
        
        readings = sensor_manager.read_all_sensors()
        
        assert len(readings) > 0
        assert all(r.is_valid for r in readings)


# tests/test_alert_engine.py

from gateway.src.alert_engine import AlertEngine, AlertRule, AlertSeverity

@pytest.fixture
def alert_engine():
    """Fixture para AlertEngine"""
    return AlertEngine(cloud_sync=None)  # Mock cloud_sync

class TestAlertEngine:
    """Test suite para AlertEngine"""
    
    def test_add_rule(self, alert_engine):
        """Test agregar regla de alerta"""
        rule = AlertRule(
            sensor_id='temp-interior',
            condition='gt',
            threshold=35,
            severity=AlertSeverity.CRITICAL
        )
        
        alert_engine.add_rule(rule)
        assert len(alert_engine.rules) == 1
    
    def test_evaluate_temperature_high(self, alert_engine):
        """Test evaluación cuando temperatura es alta"""
        rule = AlertRule(
            sensor_id='temp-interior',
            condition='gt',
            threshold=35,
            severity=AlertSeverity.CRITICAL
        )
        rule.id = 'rule-1'
        rule.description = "Temp > 35°C"
        
        alert_engine.add_rule(rule)
        alert = alert_engine.evaluate('temp-interior', 36.5)
        
        assert alert is not None
        assert alert['severity'] == 'critical'
        assert alert['value'] == 36.5
    
    def test_cooldown_prevents_duplicate_alerts(self, alert_engine):
        """Test que cooldown evita alertas duplicadas"""
        rule = AlertRule(
            sensor_id='temp-interior',
            condition='gt',
            threshold=35,
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=30
        )
        rule.id = 'rule-1'
        
        alert_engine.add_rule(rule)
        
        # Primera alerta
        alert1 = alert_engine.evaluate('temp-interior', 36.5)
        assert alert1 is not None
        
        # Segunda alerta inmediatamente
        alert2 = alert_engine.evaluate('temp-interior', 37.0)
        assert alert2 is None  # En cooldown


# tests/test_backend_api.py

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    """Obtener token de autenticación"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    return response.json()['access_token']

class TestAuthenticationAPI:
    """Test suite para autenticación"""
    
    def test_login_success(self, client):
        """Test login exitoso"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "operator@company.com",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == 200
        assert 'access_token' in response.json()
        assert response.json()['token_type'] == 'Bearer'
    
    def test_login_invalid_credentials(self, client):
        """Test login con credenciales inválidas"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "operator@company.com",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        assert response.json()['error'] == 'invalid_credentials'
    
    def test_login_user_not_found(self, client):
        """Test login con usuario inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401


class TestSensorsAPI:
    """Test suite para API de sensores"""
    
    def test_get_sensors_authenticated(self, client, auth_token):
        """Test obtener sensores autenticado"""
        response = client.get(
            "/api/v1/sensors",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'pagination' in data
    
    def test_get_sensors_unauthenticated(self, client):
        """Test obtener sensores sin autenticación"""
        response = client.get("/api/v1/sensors")
        
        assert response.status_code == 401
    
    def test_create_sensor(self, client, auth_token):
        """Test crear nuevo sensor"""
        response = client.post(
            "/api/v1/sensors",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "gateway_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Test Sensor",
                "type": "ds18b20",
                "device_id": "28-0516a42651ff",
                "unit": "°C",
                "location": "Test Location"
            }
        )
        
        assert response.status_code == 201
        assert response.json()['sensor_id'] == 'test-sensor'
```

### 2.2 Integration Tests

```python
# tests/integration/test_end_to_end_flow.py

import pytest
import time
from datetime import datetime, timedelta

class TestEndToEndFlow:
    """Test flujo completo: sensor -> gateway -> cloud -> frontend"""
    
    @pytest.fixture
    def setup_test_environment(self):
        """Setup ambiente de testing completo"""
        # 1. Crear tenant de prueba
        # 2. Crear gateway de prueba
        # 3. Registrar sensores
        # 4. Inicializar base de datos
        yield
        # Cleanup
    
    def test_sensor_reading_to_cloud_sync(self, 
                                          setup_test_environment,
                                          gateway_container,
                                          backend_container):
        """
        Test completo:
        1. Gateway lee sensor
        2. Guarda en SQLite local
        3. Sincroniza con cloud
        4. Cloud almacena en InfluxDB
        5. API devuelve datos a frontend
        """
        
        # 1. Dispara lectura en gateway
        reading_value = 25.3
        gateway_container.execute(
            "python -c 'from src.sensor_manager import SensorManager; "
            "sm = SensorManager(); sm.read_sensor(\"temp-interior\")'"
        )
        
        # 2. Verifica en SQLite local
        time.sleep(2)
        cursor = gateway_container.db.cursor()
        cursor.execute(
            "SELECT value FROM sensor_readings WHERE sensor_id='temp-interior' LIMIT 1"
        )
        result = cursor.fetchone()
        assert result[0] == reading_value
        
        # 3. Espera sincronización con cloud
        time.sleep(6)  # Sincronización cada 5 segundos en test
        
        # 4. Consulta InfluxDB
        influx_client = backend_container.influx_client
        query_result = influx_client.query(
            f'SELECT "value" FROM "sensor_readings" WHERE "sensor_id"=\'temp-interior\' LIMIT 1'
        )
        assert len(query_result) > 0
        assert float(query_result[0]['value']) == reading_value
        
        # 5. Consulta API y verifica datos
        response = backend_container.client.get(
            "/api/v1/sensors/temp-interior/readings",
            params={
                "from": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
                "to": datetime.utcnow().isoformat() + "Z"
            }
        )
        assert response.status_code == 200
        readings = response.json()['readings']
        assert len(readings) > 0
        assert readings[-1]['value'] == reading_value
    
    def test_alert_trigger_to_notification(self, setup_test_environment):
        """Test flujo de alerta: trigger -> evaluation -> notification"""
        
        # 1. Crear regla de alerta
        # 2. Leer sensor con valor que triggea alerta
        # 3. Verificar alerta creada localmente
        # 4. Verificar sincronización a cloud
        # 5. Verificar notificación enviada
        
        pass
```

---

## 3. Ciclo de Desarrollo

### 3.1 Git Workflow

```bash
# Feature branch
git checkout -b feature/sensor-ds18b20
git add gateway/src/sensor_drivers/ds18b20.py
git commit -m "feat(sensors): Add DS18B20 driver with full calibration support"
git push origin feature/sensor-ds18b20

# Create Pull Request
# Esperar reviews
# Merge a main cuando pase CI/CD

# Release
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

### 3.2 CI/CD Pipeline (.github/workflows)

```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      
      influxdb:
        image: influxdb:2.7
      
      redis:
        image: redis:7
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies (Backend)
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run backend tests
        run: |
          cd backend
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Install dependencies (Gateway)
        run: |
          cd gateway
          pip install -r requirements.txt
      
      - name: Run gateway tests
        run: |
          cd gateway
          pytest tests/
      
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run frontend tests
        run: |
          cd frontend
          npm run test
      
      - name: Build frontend
        run: |
          cd frontend
          npm run build
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

