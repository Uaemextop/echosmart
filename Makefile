# EchoSmart — Project Makefile
# Build, test, lint and package targets for all components.

.PHONY: help install gateway-lint frontend-lint lint gateway-test backend-test \
        test build deb docker-up docker-down clean

GATEWAY_DIR   = gateway
FRONTEND_DIR  = frontend
BACKEND_DIR   = backend

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────
# Install
# ──────────────────────────────────────────────
install: ## Install all dependencies
	cd $(GATEWAY_DIR) && pip install -r requirements.txt
	@if [ -f $(FRONTEND_DIR)/package.json ]; then cd $(FRONTEND_DIR) && npm ci; fi
	@if [ -f $(BACKEND_DIR)/requirements.txt ]; then cd $(BACKEND_DIR) && pip install -r requirements.txt; fi

# ──────────────────────────────────────────────
# Linting
# ──────────────────────────────────────────────
gateway-lint: ## Lint gateway Python code
	cd $(GATEWAY_DIR) && python -m py_compile src/cli.py
	cd $(GATEWAY_DIR) && python -m py_compile main.py
	cd $(GATEWAY_DIR) && python -m py_compile src/config.py
	cd $(GATEWAY_DIR) && python -m py_compile src/sensor_manager.py
	cd $(GATEWAY_DIR) && python -m py_compile src/alert_engine.py

frontend-lint: ## Lint frontend code
	@if [ -f $(FRONTEND_DIR)/package.json ]; then cd $(FRONTEND_DIR) && npm run lint; fi

lint: gateway-lint ## Run all linters

# ──────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────
gateway-test: ## Run gateway tests
	cd $(GATEWAY_DIR) && python -m pytest tests/ -v

backend-test: ## Run backend tests
	@if [ -d $(BACKEND_DIR)/tests ]; then cd $(BACKEND_DIR) && python -m pytest tests/ -v; fi

test: gateway-test ## Run all tests

# ──────────────────────────────────────────────
# Build
# ──────────────────────────────────────────────
build: ## Verify Python compilation
	cd $(GATEWAY_DIR) && python -m compileall src/ -q
	@echo "Build OK"

# ──────────────────────────────────────────────
# Debian Package
# ──────────────────────────────────────────────
deb: ## Build .deb package for the gateway
	cd $(GATEWAY_DIR) && dpkg-buildpackage -us -uc -b

# ──────────────────────────────────────────────
# Docker
# ──────────────────────────────────────────────
docker-up: ## Start services with Docker Compose
	docker compose up -d

docker-down: ## Stop Docker Compose services
	docker compose down

# ──────────────────────────────────────────────
# Clean
# ──────────────────────────────────────────────
clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -rf $(GATEWAY_DIR)/build $(GATEWAY_DIR)/*.egg-info
	rm -f $(GATEWAY_DIR)/../echosmart-gateway_*.deb
	rm -f $(GATEWAY_DIR)/../echosmart-gateway_*.changes
	rm -f $(GATEWAY_DIR)/../echosmart-gateway_*.buildinfo
	@echo "Clean OK"
