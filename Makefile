# ─────────────────────────────────────────────────────────────────────────────
# EchoSmart — Root Makefile
#
# Centralizes common developer and CI operations across all sub-projects.
# Designed to work on Ubuntu/Debian (development) and GitHub Actions CI.
#
# Usage:
#   make help          → show this help
#   make install       → install all Python dependencies
#   make test          → run all test suites
#   make build         → compile C++ binaries
#   make deb           → build .deb package
# ─────────────────────────────────────────────────────────────────────────────

# Shell
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Directories
REPO_ROOT    := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
GATEWAY_DIR  := $(REPO_ROOT)gateway
FRONTEND_DIR := $(REPO_ROOT)frontend
BACKEND_DIR  := $(REPO_ROOT)backend
CPP_DIR      := $(GATEWAY_DIR)/cpp
DEB_BUILD    := $(GATEWAY_DIR)/debian/build-cpp

# Python
PYTHON       := python3
PYTEST       := $(PYTHON) -m pytest
VENV         := $(GATEWAY_DIR)/venv
PIP          := $(VENV)/bin/pip

# Colours for terminal output
BOLD  := \033[1m
CYAN  := \033[36m
GREEN := \033[32m
YELLOW:= \033[33m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help message
	@echo ""
	@printf "$(BOLD)$(CYAN)EchoSmart Makefile$(RESET)\n"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ \
	    { printf "  $(GREEN)%-22s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Install
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: install
install: install-gateway ## Install all project dependencies

.PHONY: install-gateway
install-gateway: ## Install Python gateway dependencies
	@printf "$(CYAN)→ Installing gateway Python dependencies...$(RESET)\n"
	cd $(GATEWAY_DIR) && $(PYTHON) -m venv venv
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r $(GATEWAY_DIR)/requirements.txt --quiet
	@printf "$(GREEN)✓ Gateway dependencies installed$(RESET)\n"

.PHONY: install-frontend
install-frontend: ## Install frontend Node dependencies
	@printf "$(CYAN)→ Installing frontend dependencies...$(RESET)\n"
	cd $(FRONTEND_DIR) && npm install
	@printf "$(GREEN)✓ Frontend dependencies installed$(RESET)\n"

# ─────────────────────────────────────────────────────────────────────────────
# Lint
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: gateway-lint frontend-lint ## Run all linters

.PHONY: gateway-lint
gateway-lint: ## Lint Python gateway (flake8 + pylint)
	@printf "$(CYAN)→ Linting gateway Python code...$(RESET)\n"
	cd $(GATEWAY_DIR) && \
	    $(PYTHON) -m flake8 src/ main.py \
	        --max-line-length=100 \
	        --extend-ignore=E203,W503 \
	        || true
	@printf "$(GREEN)✓ Gateway lint complete$(RESET)\n"

.PHONY: frontend-lint
frontend-lint: ## Lint frontend (ESLint)
	@printf "$(CYAN)→ Linting frontend...$(RESET)\n"
	@if [ -f $(FRONTEND_DIR)/package.json ]; then \
	    cd $(FRONTEND_DIR) && npx eslint src/ --ext .js,.jsx,.ts,.tsx || true; \
	else \
	    echo "  (frontend not initialized — skipped)"; \
	fi
	@printf "$(GREEN)✓ Frontend lint complete$(RESET)\n"

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: gateway-test ## Run all test suites

.PHONY: gateway-test
gateway-test: ## Run gateway Python tests (pytest)
	@printf "$(CYAN)→ Running gateway tests...$(RESET)\n"
	cd $(GATEWAY_DIR) && $(PYTHON) -m pytest tests/ -v --tb=short
	@printf "$(GREEN)✓ Gateway tests passed$(RESET)\n"

.PHONY: backend-test
backend-test: ## Run backend Python tests (pytest)
	@printf "$(CYAN)→ Running backend tests...$(RESET)\n"
	@if [ -d $(BACKEND_DIR)/tests ]; then \
	    cd $(BACKEND_DIR) && $(PYTHON) -m pytest tests/ -v --tb=short; \
	else \
	    echo "  (backend tests not found — skipped)"; \
	fi
	@printf "$(GREEN)✓ Backend tests complete$(RESET)\n"

.PHONY: test-coverage
test-coverage: ## Run gateway tests with coverage report
	@printf "$(CYAN)→ Running tests with coverage...$(RESET)\n"
	cd $(GATEWAY_DIR) && $(PYTHON) -m pytest tests/ \
	    --cov=src \
	    --cov-report=term-missing \
	    --cov-report=html:htmlcov \
	    -v
	@printf "$(GREEN)✓ Coverage report: gateway/htmlcov/index.html$(RESET)\n"

# ─────────────────────────────────────────────────────────────────────────────
# Build — C++ Binaries
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: build
build: build-cpp ## Build all compiled artifacts (C++ binaries)

.PHONY: build-cpp
build-cpp: ## Build C++ binaries (native, requires g++ and cmake)
	@printf "$(CYAN)→ Building C++ binaries...$(RESET)\n"
	mkdir -p $(DEB_BUILD)
	cd $(DEB_BUILD) && cmake \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DCMAKE_INSTALL_PREFIX=/usr \
	    $(CPP_DIR)
	$(MAKE) -C $(DEB_BUILD) -j$$(nproc)
	@printf "$(GREEN)✓ C++ binaries built:$(RESET)\n"
	@ls -lh $(DEB_BUILD)/echosmart-sysinfo $(DEB_BUILD)/echosmart-sensor-read 2>/dev/null || true

.PHONY: build-cpp-arm64
build-cpp-arm64: ## Cross-compile C++ binaries for ARM64 (requires gcc-aarch64-linux-gnu)
	@printf "$(CYAN)→ Cross-compiling C++ binaries for ARM64...$(RESET)\n"
	mkdir -p $(DEB_BUILD)-arm64
	cd $(DEB_BUILD)-arm64 && cmake \
	    -DCMAKE_BUILD_TYPE=Release \
	    -DCMAKE_INSTALL_PREFIX=/usr \
	    -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc \
	    -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++ \
	    -DCMAKE_STRIP=aarch64-linux-gnu-strip \
	    $(CPP_DIR)
	$(MAKE) -C $(DEB_BUILD)-arm64 -j$$(nproc)
	@printf "$(GREEN)✓ ARM64 binaries built in $(DEB_BUILD)-arm64$(RESET)\n"

# ─────────────────────────────────────────────────────────────────────────────
# .deb Package
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: deb
deb: ## Build the .deb package (requires dpkg-buildpackage + cross-compiler)
	@printf "$(CYAN)→ Building .deb package...$(RESET)\n"
	@command -v dpkg-buildpackage >/dev/null 2>&1 || \
	    (echo "  ERROR: dpkg-buildpackage not found. Run: sudo apt-get install dpkg-dev devscripts debhelper" && exit 1)
	cd $(GATEWAY_DIR) && dpkg-buildpackage \
	    -b \
	    -us \
	    -uc \
	    --host-arch=arm64 \
	    --build-profiles=nocheck
	@printf "$(GREEN)✓ .deb package built (see parent dir of gateway/)$(RESET)\n"
	@ls -lh $(REPO_ROOT)*.deb 2>/dev/null || true

# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: docker-up
docker-up: ## Start all services with docker-compose
	@printf "$(CYAN)→ Starting docker-compose services...$(RESET)\n"
	docker compose up -d
	@printf "$(GREEN)✓ Services started$(RESET)\n"

.PHONY: docker-down
docker-down: ## Stop all docker-compose services
	@printf "$(CYAN)→ Stopping docker-compose services...$(RESET)\n"
	docker compose down
	@printf "$(GREEN)✓ Services stopped$(RESET)\n"

.PHONY: docker-logs
docker-logs: ## Follow docker-compose logs
	docker compose logs -f

# ─────────────────────────────────────────────────────────────────────────────
# Gateway Run
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: gateway-run-sim
gateway-run-sim: ## Run gateway in simulation mode (no hardware needed)
	@printf "$(CYAN)→ Starting gateway in simulation mode...$(RESET)\n"
	cd $(GATEWAY_DIR) && SIMULATION_MODE=true $(PYTHON) main.py

.PHONY: gateway-run
gateway-run: ## Run gateway with real sensors (requires hardware)
	@printf "$(CYAN)→ Starting gateway with real sensors...$(RESET)\n"
	cd $(GATEWAY_DIR) && SIMULATION_MODE=false $(PYTHON) main.py

# ─────────────────────────────────────────────────────────────────────────────
# Sensor binaries quick test (simulation)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: sensor-test-sim
sensor-test-sim: build-cpp ## Run C++ sensor binaries in simulate mode
	@printf "$(CYAN)→ Testing echosmart-sysinfo...$(RESET)\n"
	$(DEB_BUILD)/echosmart-sysinfo --pretty
	@echo ""
	@printf "$(CYAN)→ Testing echosmart-sensor-read (simulate)...$(RESET)\n"
	@for sensor in ds18b20 dht22 bh1750 soil mhz19c; do \
	    printf "  sensor: $$sensor\n"; \
	    $(DEB_BUILD)/echosmart-sensor-read --simulate $$sensor; \
	done

# ─────────────────────────────────────────────────────────────────────────────
# Clean
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove all build artifacts and caches
	@printf "$(CYAN)→ Cleaning build artifacts...$(RESET)\n"
	rm -rf $(DEB_BUILD) $(DEB_BUILD)-arm64
	find $(REPO_ROOT) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(REPO_ROOT) -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find $(REPO_ROOT) -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find $(REPO_ROOT) -name "*.pyc" -delete 2>/dev/null || true
	find $(REPO_ROOT) -name "*.deb" -delete 2>/dev/null || true
	find $(REPO_ROOT) -name "*.changes" -delete 2>/dev/null || true
	find $(REPO_ROOT) -name "*.buildinfo" -delete 2>/dev/null || true
	@printf "$(GREEN)✓ Clean complete$(RESET)\n"

.PHONY: clean-venv
clean-venv: ## Remove Python virtual environments
	rm -rf $(GATEWAY_DIR)/venv
	@printf "$(GREEN)✓ Virtual environments removed$(RESET)\n"

# ─────────────────────────────────────────────────────────────────────────────
# Release helpers
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: version
version: ## Show current version from debian/changelog
	@head -1 $(GATEWAY_DIR)/debian/changelog | grep -oP '\(\K[^)]+'

# Prevent make from treating targets as files
.PHONY: all
all: install lint test build
