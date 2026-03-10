# EchoSmart — Contribución al Proyecto

Guía para contribuir al desarrollo de EchoSmart.

---

## Cómo Contribuir

1. **Fork** del repositorio.
2. Crear una **rama** para tu cambio:
   ```bash
   git checkout -b feature/mi-mejora
   ```
3. Realizar los cambios y **commitear** con mensajes descriptivos:
   ```bash
   git commit -m "feat: agregar soporte para sensor BME280"
   ```
4. **Push** a tu fork:
   ```bash
   git push origin feature/mi-mejora
   ```
5. Abrir un **Pull Request** hacia la rama `main` del repositorio original.

---

## Convenciones de Commits

Utilizamos [Conventional Commits](https://www.conventionalcommits.org/):

| Prefijo | Uso |
|---------|-----|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `docs:` | Cambios en documentación |
| `test:` | Agregar o modificar tests |
| `refactor:` | Refactorización sin cambio funcional |
| `chore:` | Tareas de mantenimiento (dependencias, CI, etc.) |

---

## Estructura del Repositorio

```
echosmart/
├── backend/       # API FastAPI, servicios, modelos
├── frontend/      # Aplicación React
├── gateway/       # Software del gateway Raspberry Pi
├── infra/         # Configuración de infraestructura (Docker, K8s)
├── docs/          # Documentación del proyecto
└── README.md
```

---

## Estándares de Código

### Python (Backend y Gateway)
- Seguir **PEP 8**.
- Utilizar **type hints** en funciones públicas.
- Docstrings en formato Google.
- Linter: `flake8` · Formatter: `black`.

### JavaScript/TypeScript (Frontend)
- Seguir la configuración de **ESLint** del proyecto.
- Formatter: `prettier`.
- Componentes React como funciones con hooks.

### Tests
- Cada nueva funcionalidad debe incluir tests unitarios.
- Backend: `pytest`.
- Frontend: `jest` + React Testing Library.
- Cobertura mínima objetivo: 80 %.

---

## Reportar Problemas

Al crear un **issue**, incluir:

1. Descripción clara del problema o mejora propuesta.
2. Pasos para reproducir (si es un bug).
3. Comportamiento esperado vs. comportamiento actual.
4. Versión del sistema operativo, Python, Node.js, etc.

---

## Agregar un Nuevo Sensor

1. Crear el driver en `gateway/src/sensor_drivers/`.
2. Registrar el sensor en el HAL (`gateway/src/hal.py`).
3. Agregar la configuración en `sensors.json`.
4. Documentar en `docs/sensors-hardware.md`.
5. Agregar tests unitarios.

---

## Agregar un Nuevo Endpoint API

1. Crear el router en `backend/src/routers/`.
2. Crear el servicio en `backend/src/services/`.
3. Agregar esquemas Pydantic en `backend/src/schemas/`.
4. Documentar en `docs/api-testing-devops.md`.
5. Agregar tests con `FastAPI TestClient`.

---

*Volver al [Índice de Documentación](README.md)*
