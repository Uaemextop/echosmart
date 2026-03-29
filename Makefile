# ──────────────────────────────────────────────────────────────
# EchoSmart — Top-level Makefile
# ──────────────────────────────────────────────────────────────

.DEFAULT_GOAL := help

# ── Variables ────────────────────────────────────────────────
PYTHON     ?= python3
PIP        ?= pip3
PYTEST     ?= $(PYTHON) -m pytest
NPM        ?= npm
GATEWAY    := gateway
FRONTEND   := frontend
BACKEND    := backend

# ── Help ─────────────────────────────────────────────────────
.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Install ──────────────────────────────────────────────────
.PHONY: install
install: ## Install all project dependencies
	cd $(GATEWAY) && $(PIP) install -r requirements.txt
	cd $(FRONTEND) && $(NPM) ci 2>/dev/null || true

# ── Lint ─────────────────────────────────────────────────────
.PHONY: gateway-lint
gateway-lint: ## Lint gateway Python code
	cd $(GATEWAY) && $(PYTHON) -m py_compile src/cli.py
	cd $(GATEWAY) && $(PYTHON) -m py_compile src/config.py
	cd $(GATEWAY) && $(PYTHON) -m py_compile src/sensor_manager.py
	cd $(GATEWAY) && $(PYTHON) -m py_compile src/alert_engine.py
	cd $(GATEWAY) && $(PYTHON) -m py_compile main.py

.PHONY: frontend-lint
frontend-lint: ## Lint frontend code
	cd $(FRONTEND) && $(NPM) run lint 2>/dev/null || echo "No frontend lint configured"

.PHONY: lint
lint: gateway-lint frontend-lint ## Lint all code

# ── Test ─────────────────────────────────────────────────────
.PHONY: gateway-test
gateway-test: ## Run gateway unit tests
	$(PYTEST) $(GATEWAY)/tests/ -v

.PHONY: backend-test
backend-test: ## Run backend tests
	cd $(BACKEND) && $(PYTEST) tests/ -v 2>/dev/null || echo "No backend tests configured"

.PHONY: test
test: gateway-test ## Run all tests

# ── Build ────────────────────────────────────────────────────
.PHONY: build
build: lint test ## Lint + test (validation build)
	@echo "Build OK"

# ── Debian package ───────────────────────────────────────────
.PHONY: deb
deb: ## Build the .deb package for the gateway
	cd $(GATEWAY) && dpkg-buildpackage -us -uc -b
	@echo "──────────────────────────────────────"
	@echo "  .deb package created in parent dir  "
	@echo "──────────────────────────────────────"
	@ls -1 echosmart-gateway_*.deb 2>/dev/null || true

# ── Docker ───────────────────────────────────────────────────
.PHONY: docker-up
docker-up: ## Start all services with Docker Compose
	docker compose up -d

.PHONY: docker-down
docker-down: ## Stop all Docker Compose services
	docker compose down

# ── Clean ────────────────────────────────────────────────────
.PHONY: clean
clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf echosmart-gateway_*.deb echosmart-gateway_*.changes \
	       echosmart-gateway_*.buildinfo 2>/dev/null || true
	rm -rf $(GATEWAY)/debian/echosmart-gateway/ 2>/dev/null || true
