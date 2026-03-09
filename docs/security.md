# EchoSmart — Seguridad

Documentación de las prácticas, mecanismos y configuraciones de seguridad implementados en la plataforma EchoSmart.

---

## 1. Autenticación

### JWT (JSON Web Tokens)
- **Access token**: expiración de 24 horas.
- **Refresh token**: expiración de 30 días con rotación automática.
- Algoritmo de firma: **HS256** con clave secreta configurable (`JWT_SECRET_KEY`).

### Estructura del Payload JWT

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "tenant_id": "tenant-uuid",
  "role": "operator",
  "iat": 1678901200,
  "exp": 1678987600,
  "scope": ["sensors:read", "sensors:write", "alerts:read"]
}
```

### Protección de Contraseñas
- Hashing con **bcrypt** y salt aleatorio.
- Política de complejidad mínima recomendada (8+ caracteres, mayúsculas, número, símbolo).

---

## 2. Autorización

### Control de Acceso Basado en Roles (RBAC)

| Rol | Permisos |
|-----|----------|
| **Admin** | Gestión completa: usuarios, tenants, configuración global, lectura y escritura de todos los recursos |
| **Operator** | Lectura y escritura de sensores, alertas y reportes dentro de su tenant |
| **Viewer** | Solo lectura: dashboards, reportes e historial de alertas |

### Aislamiento Multi-Tenant
- Cada consulta a la base de datos incluye el filtro `tenant_id` del usuario autenticado.
- **Row-level security (RLS)** habilitado en PostgreSQL para garantizar aislamiento a nivel de fila.
- API Keys independientes por gateway, asociadas a un tenant específico.

---

## 3. Seguridad en Comunicaciones

| Capa | Mecanismo |
|------|-----------|
| API REST | HTTPS con TLS 1.3 obligatorio |
| WebSocket | WSS (WebSocket Secure) |
| MQTT (gateway → broker local) | TLS opcional en redes internas; obligatorio en enlaces cloud |
| Gateway → Cloud | HTTPS + JWT Bearer token |

### CORS
- Orígenes permitidos configurados por entorno.
- Métodos y encabezados restringidos al mínimo necesario.

### Rate Limiting
- Límite por IP en endpoints de autenticación (ej. 10 intentos / minuto).
- Límite general por usuario autenticado según tier de suscripción.

---

## 4. Protección de Datos

### En Reposo
- Cifrado de disco para volúmenes de base de datos (EBS encryption en AWS, cifrado nativo en DigitalOcean).
- Backups cifrados con AES-256.

### En Tránsito
- TLS 1.3 en todas las comunicaciones externas.
- Certificados gestionados mediante Let's Encrypt o AWS Certificate Manager.

### Retención de Datos
- Políticas de retención configurables por tenant y por tipo de dato.
- Eliminación automática de datos expirados en InfluxDB mediante retention policies.

---

## 5. Auditoría y Monitoreo

| Componente | Función |
|------------|---------|
| **Sentry** | Rastreo de errores y excepciones en backend y frontend |
| **CloudTrail** | Registro de todas las llamadas a la API |
| **Audit Log** | Tabla interna con registro de acciones de usuario (login, cambio de configuración, etc.) |
| **Prometheus** | Métricas de seguridad: intentos de login fallidos, rate limit hits, errores 4xx/5xx |

### Alertas de Seguridad
- Notificación automática ante múltiples intentos de login fallidos.
- Alerta si se detecta acceso desde IP no reconocida (opcional).

---

## 6. Checklist de Seguridad para Producción

- [ ] `JWT_SECRET_KEY` configurada con valor aleatorio de al menos 256 bits.
- [ ] HTTPS habilitado con certificado válido.
- [ ] CORS configurado solo para orígenes de producción.
- [ ] Rate limiting activo en endpoints de autenticación.
- [ ] Backups automatizados y verificados.
- [ ] Contraseñas por defecto eliminadas de todos los servicios.
- [ ] Variables de entorno sensibles almacenadas en gestor de secretos.
- [ ] Row-level security habilitado en PostgreSQL.
- [ ] Logs de auditoría activos y monitoreados.

---

*Volver al [Índice de Documentación](README.md)*
