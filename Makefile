# EchoSmart — Makefile principal
# Uso: make help

.PHONY: help install gateway-lint frontend-lint lint \
        gateway-test backend-test test \
        build deb docker-up docker-down clean

GATEWAY_DIR := gateway
FRONTEND_DIR := frontend
BACKEND_DIR := backend
DEB_VERSION := 1.0.0

##@ General
help: ## Mostrar esta ayuda
	@awk 'BEGIN {FS = ":.*##"; printf "\nEchoSmart — Comandos disponibles\n\nUso:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Instalación
install: ## Instalar dependencias de todos los módulos
	@echo "→ Instalando dependencias del gateway..."
	cd $(GATEWAY_DIR) && pip install -r requirements.txt
	@echo "→ Instalando dependencias del frontend..."
	cd $(FRONTEND_DIR) && npm ci
	@echo "→ Instalando dependencias del backend..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "✓ Dependencias instaladas"

##@ Linting
gateway-lint: ## Lint del gateway Python (flake8)
	cd $(GATEWAY_DIR) && python -m flake8 src/ --max-line-length=100 --exclude=__pycache__

frontend-lint: ## Lint del frontend JavaScript
	cd $(FRONTEND_DIR) && npm run lint --if-present

lint: gateway-lint frontend-lint ## Lint de todos los módulos

##@ Testing
gateway-test: ## Tests del gateway Python
	cd $(GATEWAY_DIR) && python -m pytest tests/ -v --tb=short

backend-test: ## Tests del backend FastAPI
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --tb=short

test: gateway-test backend-test ## Tests de todos los módulos

##@ Build
build: ## Build de producción (frontend)
	cd $(FRONTEND_DIR) && npm ci && npm run build
	@echo "✓ Frontend compilado en $(FRONTEND_DIR)/dist/"

deb: ## Construir paquete .deb del gateway
	@echo "→ Construyendo echosmart-gateway_$(DEB_VERSION)_all.deb..."
	cd $(GATEWAY_DIR) && dpkg-buildpackage -us -uc -b
	@echo "✓ Paquete .deb generado en el directorio padre de gateway/"

##@ Infraestructura
docker-up: ## Levantar infraestructura local con Docker Compose
	docker compose up -d
	@echo "✓ Servicios iniciados. Dashboard: http://localhost:3000"

docker-down: ## Detener infraestructura local
	docker compose down
	@echo "✓ Servicios detenidos"

##@ Limpieza
clean: ## Limpiar artefactos de build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(FRONTEND_DIR)/dist $(FRONTEND_DIR)/node_modules/.cache 2>/dev/null || true
	rm -rf $(GATEWAY_DIR)/.pytest_cache $(GATEWAY_DIR)/htmlcov 2>/dev/null || true
	@echo "✓ Limpieza completada"
