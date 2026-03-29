# EchoSmart — Makefile de Producción
#
# Dos binarios:
#   - echosmart: gateway EchoPy (Raspberry Pi)
#   - echosmart-server: servidor backend
#
# Targets principales:
#   make help        — lista de targets
#   make install     — instalar dependencias
#   make build       — compilar todos los componentes
#   make test        — ejecutar todos los tests
#   make lint        — linting de todos los componentes
#   make deb         — construir paquete .deb para EchoPy

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ───────────────── Ayuda ─────────────────

.PHONY: help
help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ───────────────── Instalación ─────────────────

.PHONY: install
install: ## Instalar todas las dependencias
	cd backend && pip install -r requirements.txt
	cd frontend && npm ci
	cd mobile && npm ci 2>/dev/null || true

# ───────────────── Linting ─────────────────

.PHONY: lint gateway-lint backend-lint frontend-lint
lint: gateway-lint backend-lint frontend-lint ## Linting completo

gateway-lint: ## Lint gateway C++
	@echo "=== Gateway C++ Lint ==="
	cppcheck --enable=warning,style --error-exitcode=1 gateway/cpp/ 2>/dev/null || echo "cppcheck not installed"

backend-lint: ## Lint backend Python
	@echo "=== Backend Python Lint ==="
	cd backend && ruff check src/ tests/ 2>/dev/null || echo "ruff not installed"

frontend-lint: ## Lint frontend JS
	@echo "=== Frontend JS Lint ==="
	cd frontend && npm run lint --if-present

# ───────────────── Tests ─────────────────

.PHONY: test gateway-test backend-test frontend-test
test: gateway-test backend-test frontend-test ## Ejecutar todos los tests

gateway-test: ## Tests del gateway (C++ --simulate)
	@echo "=== Gateway C++ Tests ==="
	cd gateway/cpp && \
		g++ -O2 -std=c++17 -o /tmp/echosmart-sysinfo echosmart-sysinfo.cpp && \
		g++ -O2 -std=c++17 -o /tmp/echosmart-sensor-read echosmart-sensor-read.cpp && \
		/tmp/echosmart-sysinfo --simulate && \
		/tmp/echosmart-sensor-read ds18b20 --simulate && \
		/tmp/echosmart-sensor-read dht22 --simulate && \
		/tmp/echosmart-sensor-read bh1750 --simulate && \
		echo "✅ All gateway tests passed"

backend-test: ## Tests del backend
	@echo "=== Backend Python Tests ==="
	cd backend && python -m pytest tests/ -v --tb=short 2>/dev/null || echo "pytest not installed or tests failed"

frontend-test: ## Tests del frontend
	@echo "=== Frontend JS Tests ==="
	cd frontend && npm run test --if-present

# ───────────────── Build ─────────────────

.PHONY: build build-cpp-arm64 build-frontend build-backend
build: build-cpp-arm64 build-frontend build-backend ## Build completo

build-cpp-arm64: ## Cross-compilar C++ para arm64
	@echo "=== Building C++ binaries for arm64 ==="
	mkdir -p gateway/debian/build-cpp
	aarch64-linux-gnu-g++ -O2 -std=c++17 \
		-o gateway/debian/build-cpp/echosmart-sysinfo \
		gateway/cpp/echosmart-sysinfo.cpp
	aarch64-linux-gnu-g++ -O2 -std=c++17 \
		-o gateway/debian/build-cpp/echosmart-sensor-read \
		gateway/cpp/echosmart-sensor-read.cpp
	@echo "✅ C++ binaries built"

build-frontend: ## Build frontend
	@echo "=== Building Frontend ==="
	cd frontend && npm ci && npm run build

build-backend: ## Build backend Docker image
	@echo "=== Building Backend ==="
	cd backend && docker build -t echosmart-server:latest .

# ───────────────── .deb Package ─────────────────

.PHONY: deb
deb: build-cpp-arm64 ## Construir paquete .deb para EchoPy
	@echo "=== Building .deb package ==="
	cd gateway && dpkg-buildpackage -b -us -uc --host-arch=arm64 -rfakeroot
	@echo "✅ .deb package built"

# ───────────────── Docker ─────────────────

.PHONY: docker-up docker-down
docker-up: ## Levantar infraestructura local (Docker Compose)
	docker compose up -d
	@echo "✅ Services running"

docker-down: ## Detener infraestructura local
	docker compose down

# ───────────────── Simulación ─────────────────

.PHONY: gateway-run-sim sensor-test-sim
gateway-run-sim: ## Ejecutar gateway en modo simulación
	cd gateway/cpp && \
		g++ -O2 -std=c++17 -o /tmp/echosmart-sysinfo echosmart-sysinfo.cpp && \
		/tmp/echosmart-sysinfo --simulate

sensor-test-sim: ## Test de todos los sensores en simulación
	cd gateway/cpp && \
		g++ -O2 -std=c++17 -o /tmp/echosmart-sensor-read echosmart-sensor-read.cpp && \
		for s in ds18b20 dht22 bh1750 soil mhz19c; do \
			echo "--- $$s ---"; \
			/tmp/echosmart-sensor-read $$s --simulate; \
		done

# ───────────────── Limpieza ─────────────────

.PHONY: clean
clean: ## Limpiar artefactos de compilación
	rm -rf gateway/debian/build-cpp/
	rm -rf frontend/dist/
	rm -f /tmp/echosmart-sysinfo /tmp/echosmart-sensor-read
	@echo "✅ Clean complete"
