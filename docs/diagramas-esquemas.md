# EchoSmart — Diagramas, Bocetos y Esquemas

Colección de diagramas técnicos de la plataforma **EchoSmart** renderizados con [Mermaid](https://mermaid.js.org/). Todos los diagramas se visualizan directamente en GitHub.

---

## Índice

1. [Arquitectura General (3 Capas)](#1-arquitectura-general-3-capas)
2. [Esquema de Base de Datos (ER)](#2-esquema-de-base-de-datos-er)
3. [Flujo de Lectura de Sensores (E2E)](#3-flujo-de-lectura-de-sensores-e2e)
4. [Flujo de Evaluación de Alertas](#4-flujo-de-evaluación-de-alertas)
5. [Flujo de Autenticación JWT](#5-flujo-de-autenticación-jwt)
6. [Arquitectura del Gateway (5 Capas)](#6-arquitectura-del-gateway-5-capas)
7. [Jerarquía de Tópicos MQTT](#7-jerarquía-de-tópicos-mqtt)
8. [Arquitectura de Componentes Frontend](#8-arquitectura-de-componentes-frontend)
9. [Infraestructura de Despliegue](#9-infraestructura-de-despliegue)
10. [Roadmap del Proyecto](#10-roadmap-del-proyecto)
11. [Conexiones de Sensores (Hardware)](#11-conexiones-de-sensores-hardware)
12. [Flujo de Generación de Reportes](#12-flujo-de-generación-de-reportes)

---

## 1. Arquitectura General (3 Capas)

Visión general de la arquitectura edge-to-cloud de EchoSmart: sensores → gateway → nube → clientes.

```mermaid
graph TB
    subgraph SENSORES["🌡️ Capa de Sensores"]
        S1["DS18B20<br/>Temperatura<br/>(1-Wire)"]
        S2["DHT22<br/>Temp + Humedad<br/>(GPIO)"]
        S3["BH1750<br/>Luminosidad<br/>(I2C)"]
        S4["Soil Moisture<br/>Humedad del Suelo<br/>(ADC)"]
        S5["MHZ-19C<br/>CO₂<br/>(UART)"]
    end

    subgraph GATEWAY["🔧 Capa Edge — Gateway (Raspberry Pi 4B)"]
        HAL["HAL<br/>Hardware Abstraction Layer"]
        DRIVERS["Sensor Drivers<br/>(5 tipos)"]
        MQTT_LOCAL["Mosquitto MQTT<br/>Broker Local"]
        SQLITE["SQLite<br/>Caché Local"]
        ALERT_LOCAL["Motor de Alertas<br/>Local"]
        SSDP["SSDP<br/>Auto-Discovery"]
        SYNC["Cloud Sync<br/>Manager"]
    end

    subgraph CLOUD["☁️ Capa Cloud — Backend"]
        API["API Gateway<br/>FastAPI / Express.js"]
        WS["WebSocket<br/>Server"]
        SVC_SENSOR["Sensor<br/>Service"]
        SVC_ALERT["Alert<br/>Service"]
        SVC_REPORT["Report<br/>Service"]
        SVC_USER["User<br/>Service"]
        SVC_TENANT["Tenant<br/>Service"]
        QUEUE["RabbitMQ / Bull<br/>Cola de Tareas"]
        PG["PostgreSQL 14+<br/>Datos Relacionales"]
        INFLUX["InfluxDB 2.7+<br/>Series de Tiempo"]
        REDIS["Redis 7+<br/>Caché y Sesiones"]
    end

    subgraph CLIENTES["📱 Capa Cliente"]
        WEB["React 18+<br/>Dashboard Web"]
        MOBILE["React Native<br/>iOS / Android"]
        ADMIN["Panel de<br/>Administración"]
    end

    S1 & S2 & S3 & S4 & S5 -->|GPIO / I2C / 1-Wire / UART / ADC| HAL
    HAL --> DRIVERS
    DRIVERS --> MQTT_LOCAL
    DRIVERS --> SQLITE
    MQTT_LOCAL --> ALERT_LOCAL
    SSDP -.->|Descubrimiento| DRIVERS
    SYNC -->|HTTPS + JWT + TLS| API

    API --> SVC_SENSOR & SVC_ALERT & SVC_REPORT & SVC_USER & SVC_TENANT
    SVC_SENSOR --> INFLUX
    SVC_SENSOR --> PG
    SVC_ALERT --> QUEUE
    SVC_REPORT --> QUEUE
    SVC_USER --> PG
    SVC_TENANT --> PG
    QUEUE --> REDIS
    API --> WS

    WS -->|Tiempo Real| WEB & MOBILE
    API -->|REST API| WEB & MOBILE & ADMIN

    style SENSORES fill:#e8f5e9,stroke:#2e7d32,color:#000
    style GATEWAY fill:#fff3e0,stroke:#e65100,color:#000
    style CLOUD fill:#e3f2fd,stroke:#1565c0,color:#000
    style CLIENTES fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

---

## 2. Esquema de Base de Datos (ER)

Diagrama entidad-relación del esquema PostgreSQL principal con soporte multi-tenant.

```mermaid
erDiagram
    tenants ||--o{ users : "tiene"
    tenants ||--o{ gateways : "posee"
    tenants ||--o{ alert_rules : "configura"
    tenants ||--o{ alerts : "genera"
    gateways ||--o{ sensors : "conecta"
    sensors ||--o{ readings : "produce"
    sensors ||--o{ alert_rules : "monitorea"
    alert_rules ||--o{ alerts : "dispara"
    users ||--o{ alerts : "reconoce"

    tenants {
        uuid id PK
        varchar name
        varchar slug UK
        varchar plan
        jsonb branding
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    users {
        uuid id PK
        uuid tenant_id FK
        varchar email UK
        varchar password_hash
        varchar full_name
        enum role "admin | operator | viewer"
        boolean is_active
        timestamp last_login
        timestamp created_at
    }

    gateways {
        uuid id PK
        uuid tenant_id FK
        varchar name
        varchar location
        varchar firmware_version
        enum status "online | offline | maintenance"
        jsonb config
        timestamp last_seen
        timestamp created_at
    }

    sensors {
        uuid id PK
        uuid gateway_id FK
        enum type "ds18b20 | dht22 | bh1750 | soil_moisture | mhz19c"
        varchar name
        varchar unit
        integer polling_interval_s
        boolean is_active
        float last_value
        timestamp last_reading_at
        timestamp created_at
    }

    readings {
        bigint id PK
        uuid sensor_id FK
        float value
        varchar unit
        integer quality
        timestamp recorded_at
    }

    alert_rules {
        uuid id PK
        uuid tenant_id FK
        uuid sensor_id FK
        varchar name
        enum severity "info | warning | critical"
        varchar condition "gt | lt | eq | gte | lte"
        float threshold
        integer duration_s
        integer cooldown_s
        boolean is_active
        timestamp created_at
    }

    alerts {
        uuid id PK
        uuid tenant_id FK
        uuid rule_id FK
        uuid sensor_id FK
        enum severity "info | warning | critical"
        enum status "active | acknowledged | resolved"
        float trigger_value
        uuid acknowledged_by FK
        timestamp triggered_at
        timestamp resolved_at
    }
```

---

## 3. Flujo de Lectura de Sensores (E2E)

Secuencia completa desde la lectura física del sensor hasta la visualización en el dashboard.

```mermaid
sequenceDiagram
    autonumber
    participant Sensor as 🌡️ Sensor Físico
    participant Driver as 📟 Sensor Driver
    participant HAL as ⚙️ HAL
    participant SQLite as 💾 SQLite Cache
    participant MQTT as 📡 MQTT Broker
    participant Sync as 🔄 Cloud Sync
    participant API as ☁️ Backend API
    participant Queue as 📬 RabbitMQ
    participant Worker as 👷 Worker
    participant InfluxDB as 📊 InfluxDB
    participant Redis as ⚡ Redis
    participant WS as 🔌 WebSocket
    participant Dashboard as 📱 Dashboard

    Sensor->>HAL: Señal eléctrica (GPIO/I2C/1-Wire/UART)
    HAL->>Driver: Datos crudos del bus
    Driver->>Driver: Validar y convertir unidades
    Driver->>SQLite: Guardar lectura (caché local)
    Driver->>MQTT: Publicar en tópico local
    MQTT->>Sync: Notificar nueva lectura

    alt Conectividad disponible
        Sync->>API: POST /api/v1/readings (batch, JSON comprimido)
        API->>API: Validar JWT + tenant_id
        API->>Queue: Encolar para procesamiento async
        Queue->>Worker: Consumir mensaje
        Worker->>InfluxDB: Insertar serie de tiempo
        Worker->>Redis: Actualizar sensor:latest:{id}
        Worker->>Worker: Evaluar reglas de alerta
        Worker->>WS: Emitir evento readings.new
        WS->>Dashboard: Push tiempo real
        Dashboard->>Dashboard: Actualizar gráfica
    else Sin conectividad
        Sync->>SQLite: Acumular en buffer offline
        Note over Sync,SQLite: Reintentar al recuperar conexión
    end
```

---

## 4. Flujo de Evaluación de Alertas

Máquina de estados del ciclo de vida de una alerta y el proceso de evaluación.

```mermaid
stateDiagram-v2
    [*] --> NORMAL: Sensor activo

    NORMAL --> EVALUANDO: Nueva lectura recibida
    EVALUANDO --> NORMAL: Valor dentro de rango
    EVALUANDO --> ALERTA: Umbral superado

    ALERTA --> NOTIFICANDO: Primera ocurrencia
    NOTIFICANDO --> ALERTA_ACTIVA: Notificaciones enviadas

    ALERTA_ACTIVA --> ESCALADA: Sin respuesta (timeout)
    ALERTA_ACTIVA --> RECONOCIDA: Operador reconoce
    ALERTA_ACTIVA --> RESUELTA: Valor vuelve a rango normal

    ESCALADA --> CRITICA: Persistencia > duración máxima
    ESCALADA --> RECONOCIDA: Operador reconoce

    CRITICA --> RECONOCIDA: Acción tomada
    RECONOCIDA --> RESUELTA: Problema corregido
    RECONOCIDA --> ESCALADA: Problema persiste

    RESUELTA --> [*]: Alerta cerrada

    note right of NORMAL: Monitoreo continuo<br/>cada polling_interval_s
    note right of NOTIFICANDO: Email, SMS,<br/>Push, Webhook
    note left of CRITICA: Notificación a<br/>todos los admins
```

### Condiciones de Evaluación

```mermaid
graph LR
    subgraph Tipos["Tipos de Condición"]
        SIMPLE["Simple<br/>valor > umbral"]
        DURACION["Duración<br/>valor > umbral por N seg"]
        COMPUESTA["Compuesta<br/>temp > 30 AND hum < 40"]
        HISTERESIS["Histéresis<br/>activa: >30°C<br/>desactiva: <28°C"]
    end

    subgraph Canales["Canales de Notificación"]
        EMAIL["📧 Email<br/>(SendGrid)"]
        SMS["📱 SMS<br/>(Twilio)"]
        PUSH["🔔 Push<br/>(FCM)"]
        WEBHOOK["🔗 Webhook"]
        INAPP["💬 In-App"]
    end

    SIMPLE & DURACION & COMPUESTA & HISTERESIS --> EMAIL & SMS & PUSH & WEBHOOK & INAPP

    style Tipos fill:#fff8e1,stroke:#f57f17,color:#000
    style Canales fill:#e8eaf6,stroke:#283593,color:#000
```

---

## 5. Flujo de Autenticación JWT

Secuencia de autenticación, autorización y refresco de tokens.

```mermaid
sequenceDiagram
    autonumber
    participant Client as 📱 Cliente
    participant API as ☁️ API Gateway
    participant Auth as 🔐 Auth Service
    participant DB as 🗄️ PostgreSQL
    participant Redis as ⚡ Redis

    Note over Client,Redis: Login Inicial

    Client->>API: POST /auth/login {email, password}
    API->>Auth: Validar credenciales
    Auth->>DB: SELECT user WHERE email = ?
    DB-->>Auth: User record
    Auth->>Auth: bcrypt.compare(password, hash)

    alt Credenciales válidas
        Auth->>Auth: Generar JWT (sub, email, tenant_id, role)
        Auth->>Redis: Guardar sesión (session:{user_id}, TTL 30d)
        Auth-->>API: {access_token, refresh_token}
        API-->>Client: 200 OK + HttpOnly cookie (refresh)
    else Credenciales inválidas
        Auth-->>API: Error de autenticación
        API-->>Client: 401 Unauthorized
    end

    Note over Client,Redis: Petición Protegida

    Client->>API: GET /api/v1/sensors (Authorization: Bearer {token})
    API->>API: Verificar firma JWT
    API->>API: Verificar expiración
    API->>Redis: Verificar blacklist
    API->>API: Extraer tenant_id y role
    API->>API: Verificar permisos RBAC

    alt Token válido + permisos OK
        API-->>Client: 200 OK + datos filtrados por tenant
    else Token expirado
        Client->>API: POST /auth/refresh (cookie refresh_token)
        API->>Auth: Validar refresh_token
        Auth->>Redis: Verificar sesión activa
        Auth-->>API: Nuevo access_token
        API-->>Client: 200 OK + nuevo access_token
    end
```

### Jerarquía RBAC

```mermaid
graph TD
    SA["👑 SUPERADMIN<br/>Gestión global de tenants"]
    TA["🏢 TENANT_ADMIN<br/>Gestión de usuarios y gateways"]
    OP["👤 OPERATOR<br/>Sensores y alertas"]
    VW["👁️ VIEWER<br/>Solo lectura"]

    SA --> TA --> OP --> VW

    SA -.-|"Crear/eliminar tenants<br/>Acceso total"| SA_P["Todos los permisos"]
    TA -.-|"CRUD usuarios<br/>Config gateways y alertas"| TA_P["Permisos del tenant"]
    OP -.-|"Ver sensores<br/>Reconocer alertas"| OP_P["Permisos operativos"]
    VW -.-|"Dashboards<br/>Reportes"| VW_P["Permisos de lectura"]

    style SA fill:#ffcdd2,stroke:#b71c1c,color:#000
    style TA fill:#fff9c4,stroke:#f57f17,color:#000
    style OP fill:#c8e6c9,stroke:#2e7d32,color:#000
    style VW fill:#e3f2fd,stroke:#1565c0,color:#000
```

---

## 6. Arquitectura del Gateway (5 Capas)

Diagrama de la arquitectura de software del gateway (Raspberry Pi) con sus 5 capas funcionales.

```mermaid
graph TB
    subgraph L5["Capa 5 — Orquestación"]
        MAIN["main.py<br/>Orquestador Principal"]
        DISCOVERY["SSDP Discovery<br/>Auto-detección de sensores"]
        CLOUDSYNC["Cloud Sync Manager<br/>Sincronización con nube"]
        ALERTENG["Alert Engine<br/>Evaluación local de reglas"]
        SCHEDULER["Scheduler<br/>Polling de sensores"]
    end

    subgraph L4["Capa 4 — Drivers de Sensores"]
        DRV_TEMP["DS18B20 Driver<br/>Temperatura (1-Wire)"]
        DRV_DHT["DHT22 Driver<br/>Temp + Humedad (GPIO)"]
        DRV_LUX["BH1750 Driver<br/>Luminosidad (I2C)"]
        DRV_SOIL["Soil Moisture Driver<br/>Hum. Suelo (ADC)"]
        DRV_CO2["MHZ-19C Driver<br/>CO₂ (UART)"]
    end

    subgraph L3["Capa 3 — HAL (Hardware Abstraction Layer)"]
        GPIO["GPIO Manager<br/>setup / read / write"]
        I2C["I2C Manager<br/>bus scan / read / write"]
        WIRE["1-Wire Interface<br/>device discovery / read"]
        ADC["ADC Reader<br/>(ADS1115 vía I2C)"]
        UART_M["UART Manager<br/>serial read / write"]
    end

    subgraph L2["Capa 2 — Persistencia y Mensajería"]
        SQLITE_G["SQLite 3<br/>Caché local de lecturas"]
        MQTT_G["Mosquitto MQTT<br/>Broker local (puerto 1883)"]
        CONFIG["config.yaml<br/>Configuración del gateway"]
    end

    subgraph L1["Capa 1 — Sistema Operativo"]
        OS["Raspberry Pi OS<br/>(64-bit, Lite)"]
        SYSTEMD["systemd<br/>Servicios del sistema"]
        NETWORK["NetworkManager<br/>Conectividad WiFi/Ethernet"]
    end

    MAIN --> DISCOVERY & CLOUDSYNC & ALERTENG & SCHEDULER
    SCHEDULER --> DRV_TEMP & DRV_DHT & DRV_LUX & DRV_SOIL & DRV_CO2

    DRV_TEMP --> WIRE
    DRV_DHT --> GPIO
    DRV_LUX --> I2C
    DRV_SOIL --> ADC
    DRV_CO2 --> UART_M

    GPIO & I2C & WIRE & ADC & UART_M --> OS

    DRV_TEMP & DRV_DHT & DRV_LUX & DRV_SOIL & DRV_CO2 --> SQLITE_G
    DRV_TEMP & DRV_DHT & DRV_LUX & DRV_SOIL & DRV_CO2 --> MQTT_G

    ALERTENG --> MQTT_G
    CLOUDSYNC --> SQLITE_G

    SYSTEMD --> MAIN
    NETWORK --> CLOUDSYNC

    style L5 fill:#e8eaf6,stroke:#283593,color:#000
    style L4 fill:#e0f2f1,stroke:#00695c,color:#000
    style L3 fill:#fff3e0,stroke:#e65100,color:#000
    style L2 fill:#fce4ec,stroke:#880e4f,color:#000
    style L1 fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

---

## 7. Jerarquía de Tópicos MQTT

Estructura de tópicos MQTT utilizados para la comunicación interna del gateway y hacia la nube.

```mermaid
graph LR
    ROOT["echosmart/"]

    ROOT --> GW["{gateway_id}/"]

    GW --> SENSORS["sensors/"]
    GW --> ALERTS["alerts/"]
    GW --> SYSTEM["system/"]

    SENSORS --> SID["{sensor_id}/"]
    SID --> DATA["data<br/>📊 Lecturas"]
    SID --> STATUS_S["status<br/>🟢 Estado del sensor"]

    ALERTS --> AID["{alert_id}<br/>🚨 Alerta disparada"]

    SYSTEM --> SYS_STATUS["status<br/>💓 Heartbeat del gateway"]
    SYSTEM --> SYS_CONFIG["config<br/>⚙️ Configuración remota"]
    SYSTEM --> SYS_CMD["command<br/>🎮 Comandos remotos"]

    subgraph Payload_Lectura["Payload — Lectura"]
        PL["sensor_id: string<br/>type: enum<br/>value: float<br/>unit: string<br/>timestamp: ISO8601<br/>quality: 0-100"]
    end

    subgraph Payload_Alerta["Payload — Alerta"]
        PA["alert_id: uuid<br/>sensor_id: string<br/>rule_id: uuid<br/>severity: enum<br/>condition: string<br/>current_value: float<br/>threshold: float"]
    end

    DATA -.-> Payload_Lectura
    AID -.-> Payload_Alerta

    style ROOT fill:#e3f2fd,stroke:#1565c0,color:#000
    style Payload_Lectura fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Payload_Alerta fill:#ffebee,stroke:#c62828,color:#000
```

**Configuración MQTT:**

| Parámetro | Valor |
|-----------|-------|
| Protocolo | MQTT 3.1.1 |
| Broker | Mosquitto 2.0+ |
| Puerto local | 1883 |
| Puerto TLS | 8883 |
| QoS | 1 (al menos una vez) |
| Retain | Habilitado para status |

---

## 8. Arquitectura de Componentes Frontend

Estructura de componentes React y flujo de datos con Redux Toolkit.

```mermaid
graph TB
    subgraph App["🌐 App (React 18 + Vite)"]
        ROUTER["React Router<br/>Navegación SPA"]

        subgraph Pages["Páginas"]
            DASH["Dashboard"]
            SENSOR_P["Sensores"]
            ALERT_P["Centro de Alertas"]
            REPORT_P["Reportes"]
            ADMIN_P["Administración"]
            LOGIN_P["Login"]
        end

        subgraph Components["Componentes Reutilizables"]
            subgraph Charts_C["📈 Charts"]
                TEMP_CH["TemperatureChart"]
                HUM_CH["HumidityChart"]
                COMP_CH["ComparisonChart"]
                HEAT_CH["HeatmapChart"]
            end

            subgraph Sensors_C["🌡️ Sensors"]
                SENSOR_LIST["SensorList"]
                SENSOR_MODAL["SensorModal"]
                SENSOR_DETAIL["DetailPanel"]
                SENSOR_IND["StatusIndicator"]
            end

            subgraph Alerts_C["🚨 Alerts"]
                ALERT_CENTER["AlertCenter"]
                ALERT_RULE["RuleEditor"]
                ALERT_HIST["AlertHistory"]
                ALERT_BANNER["AlertBanner"]
            end

            subgraph Common_C["🧩 Common"]
                HEADER["Header"]
                SIDEBAR["Sidebar"]
                FOOTER["Footer"]
                SPINNER["LoadingSpinner"]
                ERROR_B["ErrorBoundary"]
                TOAST["ToastNotification"]
            end
        end

        subgraph State["📦 Redux Toolkit Store"]
            S_SENSORS["sensorsSlice<br/>{data, loading, error}"]
            S_READINGS["readingsSlice<br/>{data[sensor_id]}"]
            S_ALERTS["alertsSlice<br/>{data, filters}"]
            S_AUTH["authSlice<br/>{user, token}"]
            S_UI["uiSlice<br/>{theme, sidebar}"]
        end

        subgraph Services["🔌 Servicios"]
            AXIOS["Axios<br/>HTTP Client"]
            WS_CLIENT["WebSocket<br/>Client"]
            I18N["i18n<br/>Internacionalización"]
        end
    end

    ROUTER --> Pages
    DASH --> Charts_C & Sensors_C
    SENSOR_P --> Sensors_C
    ALERT_P --> Alerts_C
    Pages --> Common_C

    Components -->|dispatch / useSelector| State
    State -->|acciones async| Services
    AXIOS -->|REST API| API_EXT["☁️ Backend API"]
    WS_CLIENT -->|Tiempo real| WS_EXT["🔌 WebSocket Server"]

    style App fill:#f5f5f5,stroke:#424242,color:#000
    style Pages fill:#e3f2fd,stroke:#1565c0,color:#000
    style State fill:#fff3e0,stroke:#e65100,color:#000
    style Services fill:#e8f5e9,stroke:#2e7d32,color:#000
```

---

## 9. Infraestructura de Despliegue

Diagrama de la infraestructura de producción con Docker, Kubernetes y servicios cloud.

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        USERS["👥 Usuarios"]
        GW_FIELD["🔧 Gateways<br/>(Invernaderos)"]
    end

    subgraph CDN_LB["Capa de Entrada"]
        CDN["CloudFront / CDN<br/>Archivos estáticos"]
        LB["Load Balancer<br/>(Nginx / ALB)"]
        CERT["TLS/SSL<br/>Let's Encrypt"]
    end

    subgraph K8S["☸️ Kubernetes Cluster"]
        subgraph Backend_Pods["Backend Pods (×3 réplicas)"]
            B1["FastAPI #1"]
            B2["FastAPI #2"]
            B3["FastAPI #3"]
        end

        subgraph Workers["Worker Pods"]
            W1["Worker Alertas"]
            W2["Worker Reportes"]
            W3["Worker Sync"]
        end

        subgraph Frontend_Pod["Frontend Pod"]
            F1["React App<br/>(Nginx static)"]
        end
    end

    subgraph Data["🗄️ Capa de Datos"]
        PG_DB["PostgreSQL 14+<br/>(RDS Multi-AZ)"]
        INFLUX_DB["InfluxDB 2.7+<br/>(Series de tiempo)"]
        REDIS_DB["Redis 7+<br/>(ElastiCache)"]
        RABBIT["RabbitMQ<br/>(Cola de mensajes)"]
        S3["S3 / Spaces<br/>(Reportes PDF/Excel)"]
    end

    subgraph Monitoring["📊 Monitoreo"]
        PROM["Prometheus<br/>Métricas"]
        GRAF["Grafana<br/>Dashboards"]
        LOGS["ELK Stack<br/>Logs centralizados"]
    end

    USERS -->|HTTPS| CDN
    USERS -->|HTTPS| LB
    GW_FIELD -->|HTTPS + JWT| LB
    CDN --> F1
    CERT --> LB
    LB --> B1 & B2 & B3
    B1 & B2 & B3 --> RABBIT
    RABBIT --> W1 & W2 & W3
    B1 & B2 & B3 --> PG_DB & INFLUX_DB & REDIS_DB
    W1 & W2 & W3 --> PG_DB & INFLUX_DB & S3
    B1 & B2 & B3 --> PROM
    PROM --> GRAF
    B1 & B2 & B3 --> LOGS

    style Internet fill:#e3f2fd,stroke:#1565c0,color:#000
    style CDN_LB fill:#fff8e1,stroke:#f57f17,color:#000
    style K8S fill:#e8f5e9,stroke:#2e7d32,color:#000
    style Data fill:#fce4ec,stroke:#880e4f,color:#000
    style Monitoring fill:#f3e5f5,stroke:#6a1b9a,color:#000
```

### Docker Compose (Desarrollo Local)

```mermaid
graph LR
    subgraph docker_compose["🐳 Docker Compose — Desarrollo Local"]
        FE["frontend<br/>:3000"]
        BE["backend<br/>:8000"]
        PG_L["postgres<br/>:5432"]
        INF_L["influxdb<br/>:8086"]
        RED_L["redis<br/>:6379"]
        MOSQ["mosquitto<br/>:1883"]
    end

    FE -->|API calls| BE
    BE --> PG_L & INF_L & RED_L
    BE -->|MQTT subscribe| MOSQ

    style docker_compose fill:#e3f2fd,stroke:#1565c0,color:#000
```

---

## 10. Roadmap del Proyecto

Línea de tiempo de las 5 fases de implementación de EchoSmart.

```mermaid
gantt
    title EchoSmart — Roadmap de Implementación
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Fase 1 — MVP Gateway
        Configuración Raspberry Pi OS          :done, f1a, 2026-01-06, 5d
        Drivers de sensores (DS18B20, DHT22, BH1750) :done, f1b, after f1a, 7d
        HAL y abstracción de hardware          :done, f1c, after f1a, 7d
        SQLite caché local                     :done, f1d, after f1b, 3d
        MQTT broker local (Mosquitto)          :done, f1e, after f1d, 3d
        Motor de alertas local                 :done, f1f, after f1e, 4d

    section Fase 2 — Cloud Backend
        FastAPI setup + auth JWT               :active, f2a, 2026-01-27, 5d
        PostgreSQL schema + migraciones        :active, f2b, after f2a, 5d
        InfluxDB integración                   :f2c, after f2b, 5d
        API REST sensores y alertas            :f2d, after f2b, 7d
        Cloud Sync gateway-nube                :f2e, after f2c, 5d
        RabbitMQ + workers async               :f2f, after f2d, 5d

    section Fase 3 — Frontend Web
        React + Vite setup                     :f3a, 2026-03-02, 3d
        Dashboard con gráficas tiempo real     :f3b, after f3a, 7d
        Gestión de sensores y alertas          :f3c, after f3b, 7d
        Panel de administración                :f3d, after f3c, 5d
        WebSocket tiempo real                  :f3e, after f3a, 10d

    section Fase 4 — Mobile
        React Native (Expo) setup              :f4a, 2026-04-06, 5d
        Dashboard mobile                       :f4b, after f4a, 10d
        Push notifications (FCM)               :f4c, after f4b, 5d
        Alertas mobile                         :f4d, after f4b, 7d

    section Fase 5 — Avanzado
        Generación de reportes PDF/Excel       :f5a, 2026-05-04, 7d
        Control de actuadores                  :f5b, after f5a, 10d
        ML predicción de temperatura           :f5c, after f5a, 14d
        Detección de anomalías                 :f5d, after f5c, 10d
```

---

## 11. Conexiones de Sensores (Hardware)

Diagrama de conexiones físicas entre los sensores y la Raspberry Pi 4B.

```mermaid
graph LR
    subgraph RPI["🔧 Raspberry Pi 4B — GPIO Header"]
        PIN1["Pin 1 — 3.3V"]
        PIN2["Pin 2 — 5V"]
        PIN6["Pin 6 — GND"]
        PIN7["Pin 7 — GPIO4"]
        PIN9["Pin 9 — GND"]
        PIN11["Pin 11 — GPIO17"]
        PIN3["Pin 3 — SDA (I2C)"]
        PIN5["Pin 5 — SCL (I2C)"]
        PIN8["Pin 8 — TXD (UART)"]
        PIN10["Pin 10 — RXD (UART)"]
    end

    subgraph S_TEMP["🌡️ DS18B20 — Temperatura"]
        DS_VDD["VDD → 3.3V"]
        DS_DQ["DQ → GPIO4 + R 4.7kΩ"]
        DS_GND["GND → GND"]
    end

    subgraph S_DHT["💧 DHT22 — Temp + Humedad"]
        DHT_VCC["VCC → 3.3V"]
        DHT_DATA["DATA → GPIO17 + R 10kΩ"]
        DHT_GND["GND → GND"]
    end

    subgraph S_LUX["☀️ BH1750 — Luminosidad"]
        BH_VCC["VCC → 3.3V"]
        BH_SDA["SDA → SDA (I2C)"]
        BH_SCL["SCL → SCL (I2C)"]
        BH_GND["GND → GND"]
        BH_ADDR["ADDR → GND (0x23)"]
    end

    subgraph S_SOIL["🌱 Soil Moisture — Hum. Suelo"]
        SOIL_VCC["VCC → 3.3V"]
        SOIL_AO["AO → ADS1115 A0"]
        SOIL_GND["GND → GND"]
    end

    subgraph S_CO2["💨 MHZ-19C — CO₂"]
        CO2_VIN["VIN → 5V"]
        CO2_TX["TX → RXD (UART)"]
        CO2_RX["RX → TXD (UART)"]
        CO2_GND["GND → GND"]
    end

    subgraph ADC["📟 ADS1115 — ADC (I2C)"]
        ADS_VCC["VCC → 3.3V"]
        ADS_SDA["SDA → SDA (I2C)"]
        ADS_SCL["SCL → SCL (I2C)"]
        ADS_GND["GND → GND"]
        ADS_A0["A0 ← Soil Moisture"]
    end

    DS_VDD --> PIN1
    DS_DQ --> PIN7
    DS_GND --> PIN6

    DHT_VCC --> PIN1
    DHT_DATA --> PIN11
    DHT_GND --> PIN9

    BH_VCC --> PIN1
    BH_SDA --> PIN3
    BH_SCL --> PIN5
    BH_GND --> PIN6

    SOIL_AO --> ADS_A0
    SOIL_VCC --> PIN1
    SOIL_GND --> PIN6

    ADS_VCC --> PIN1
    ADS_SDA --> PIN3
    ADS_SCL --> PIN5
    ADS_GND --> PIN6

    CO2_VIN --> PIN2
    CO2_TX --> PIN10
    CO2_RX --> PIN8
    CO2_GND --> PIN9

    style RPI fill:#c8e6c9,stroke:#2e7d32,color:#000
    style S_TEMP fill:#ffcdd2,stroke:#c62828,color:#000
    style S_DHT fill:#bbdefb,stroke:#1565c0,color:#000
    style S_LUX fill:#fff9c4,stroke:#f57f17,color:#000
    style S_SOIL fill:#d7ccc8,stroke:#4e342e,color:#000
    style S_CO2 fill:#e1bee7,stroke:#6a1b9a,color:#000
    style ADC fill:#b2dfdb,stroke:#00695c,color:#000
```

### Especificaciones de Sensores

| Sensor | Protocolo | Dirección | Rango | Precisión | Polling |
|--------|-----------|-----------|-------|-----------|---------|
| DS18B20 | 1-Wire | GPIO4 | -55°C a +125°C | ±0.5°C | 1s |
| DHT22 | GPIO | GPIO17 | -40°C a +80°C / 0-100% RH | ±0.5°C / ±2% | 2s |
| BH1750 | I2C | 0x23 | 1 – 65535 lux | ±1 lux | 1s |
| Soil Moisture | ADC (ADS1115) | 0x48 A0 | 0 – 100% | ±2% | 5s |
| MHZ-19C | UART | /dev/ttyS0 | 400 – 5000 ppm | ±50 ppm | 5s |

---

## 12. Flujo de Generación de Reportes

Secuencia del proceso asíncrono de generación de reportes PDF/Excel.

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Usuario
    participant FE as 📱 Frontend
    participant API as ☁️ API Backend
    participant Queue as 📬 RabbitMQ
    participant Worker as 👷 Report Worker
    participant InfluxDB as 📊 InfluxDB
    participant PG as 🗄️ PostgreSQL
    participant S3 as 📁 S3 Storage
    participant Redis as ⚡ Redis
    participant WS as 🔌 WebSocket

    User->>FE: Solicitar reporte (tipo, fechas, sensores)
    FE->>API: POST /api/v1/reports
    API->>PG: Crear registro report (status: pending)
    API->>Queue: Encolar tarea de generación
    API-->>FE: 202 Accepted {report_id}
    FE->>FE: Mostrar indicador de progreso

    Queue->>Worker: Consumir tarea
    Worker->>InfluxDB: Query datos del período
    Worker->>PG: Query metadatos (sensores, alertas)
    Worker->>Worker: Generar gráficas (matplotlib)
    Worker->>Worker: Compilar PDF o Excel

    alt Generación exitosa
        Worker->>S3: Subir archivo generado
        Worker->>PG: Actualizar status: completed, file_url
        Worker->>Redis: Publicar evento report.ready
        Redis->>WS: Broadcast a cliente
        WS->>FE: Notificación: reporte listo
        FE->>User: Mostrar botón de descarga
        User->>FE: Descargar reporte
        FE->>API: GET /api/v1/reports/{id}/download
        API->>S3: Obtener archivo
        S3-->>API: Archivo PDF/Excel
        API-->>FE: Descarga del archivo
    else Error en generación
        Worker->>PG: Actualizar status: failed, error_message
        Worker->>Redis: Publicar evento report.failed
        Redis->>WS: Broadcast a cliente
        WS->>FE: Notificación: error en reporte
        FE->>User: Mostrar mensaje de error
    end
```

---

## Convenciones

- Todos los diagramas utilizan [Mermaid](https://mermaid.js.org/) y se renderizan nativamente en GitHub.
- Los colores siguen el esquema: 🟢 Edge/Gateway, 🔵 Cloud/Backend, 🟣 Frontend/Clientes, 🔴 Alertas/Errores, 🟡 Datos/Storage.
- Los diagramas complementan la documentación detallada disponible en los archivos individuales del directorio `docs/`.

---

*Última actualización: Marzo 2026 · EchoSmart Dev Team*
