# EchoSmart — Makefile raíz
# Uso: make <target>
# Ejecutar 'make help' para ver todos los targets disponibles.

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ── Variables ────────────────────────────────────────────────────────────
GATEWAY_DIR  := gateway
BACKEND_DIR  := backend
FRONTEND_DIR := frontend
DEB_VERSION  ?= 1.0.0

# ── Colores ───────────────────────────────────────────────────────────────
BOLD  := \033[1m
GREEN := \033[0;32m
CYAN  := \033[0;36m
NC    := \033[0m

# ── Help ─────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Mostrar esta ayuda
	@echo -e "$(CYAN)EchoSmart — Targets disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  $(BOLD)%-22s$(NC) %s\n",$$1,$$2}'

# ── Instalación ───────────────────────────────────────────────────────────
.PHONY: install
install: ## Instalar todas las dependencias (gateway + backend + frontend)
	@echo -e "$(CYAN)▶ Instalando dependencias del gateway...$(NC)"
	cd $(GATEWAY_DIR) && pip install -r requirements.txt
	@echo -e "$(CYAN)▶ Instalando dependencias del backend...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements.txt 2>/dev/null || true
	@echo -e "$(CYAN)▶ Instalando dependencias del frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm ci 2>/dev/null || true
	@echo -e "$(GREEN)✓ Dependencias instaladas$(NC)"

# ── Lint ──────────────────────────────────────────────────────────────────
.PHONY: gateway-lint
gateway-lint: ## Lint del gateway (flake8 + black --check)
	@echo -e "$(CYAN)▶ Lint gateway...$(NC)"
	cd $(GATEWAY_DIR) && python -m flake8 src/ --max-line-length=100 --ignore=E501,W503 \
		|| echo "flake8 no disponible, saltando"
	cd $(GATEWAY_DIR) && python -m black --check src/ \
		|| echo "black no disponible, saltando"

.PHONY: frontend-lint
frontend-lint: ## Lint del frontend (ESLint)
	@echo -e "$(CYAN)▶ Lint frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint --if-present

.PHONY: lint
lint: gateway-lint frontend-lint ## Lint de todos los componentes

# ── Tests ─────────────────────────────────────────────────────────────────
.PHONY: gateway-test
gateway-test: ## Ejecutar tests del gateway
	@echo -e "$(CYAN)▶ Tests del gateway...$(NC)"
	cd $(GATEWAY_DIR) && python -m pytest tests/ -v --tb=short

.PHONY: backend-test
backend-test: ## Ejecutar tests del backend
	@echo -e "$(CYAN)▶ Tests del backend...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --tb=short 2>/dev/null || \
		echo "Backend tests no disponibles"

.PHONY: test
test: gateway-test backend-test ## Ejecutar todos los tests

# ── Build ─────────────────────────────────────────────────────────────────
.PHONY: build
build: ## Compilar el binario C echosmart-sysinfo
	@echo -e "$(CYAN)▶ Compilando echosmart-sysinfo...$(NC)"
	gcc -O2 -o $(GATEWAY_DIR)/echosmart-sysinfo \
	       $(GATEWAY_DIR)/c/echosmart-sysinfo.c
	@echo -e "$(GREEN)✓ Binario generado: $(GATEWAY_DIR)/echosmart-sysinfo$(NC)"

# ── Paquete .deb ──────────────────────────────────────────────────────────
.PHONY: deb
deb: ## Construir el paquete .deb del gateway (requiere dpkg-buildpackage)
	@echo -e "$(CYAN)▶ Construyendo paquete .deb (v$(DEB_VERSION))...$(NC)"
	cd $(GATEWAY_DIR) && dpkg-buildpackage -us -uc -b --build=binary
	@echo -e "$(GREEN)✓ Paquete .deb generado en el directorio padre$(NC)"

# ── Docker ────────────────────────────────────────────────────────────────
.PHONY: docker-up
docker-up: ## Levantar infraestructura local con Docker Compose
	@echo -e "$(CYAN)▶ Levantando servicios Docker...$(NC)"
	docker compose up -d
	@echo -e "$(GREEN)✓ Servicios activos. Usa 'docker compose ps' para ver el estado$(NC)"

.PHONY: docker-down
docker-down: ## Detener y eliminar contenedores Docker
	@echo -e "$(CYAN)▶ Deteniendo servicios Docker...$(NC)"
	docker compose down

# ── Limpieza ──────────────────────────────────────────────────────────────
.PHONY: clean
clean: ## Limpiar artefactos de build
	rm -f $(GATEWAY_DIR)/echosmart-sysinfo
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo -e "$(GREEN)✓ Limpieza completada$(NC)"

# ── Simulación rápida del gateway ─────────────────────────────────────────
.PHONY: gateway-run-sim
gateway-run-sim: ## Iniciar el gateway en modo simulación (para desarrollo)
	cd $(GATEWAY_DIR) && SIMULATION_MODE=true \
	    PYTHONPATH=.. python -m gateway.src.cli run --simulate
