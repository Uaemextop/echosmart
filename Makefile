# ─────────────────────────────────────────────────────────────
# EchoSmart — Root Makefile
# Targets for development, testing, packaging, and deployment
# ─────────────────────────────────────────────────────────────

.PHONY: help install lint test build deb clean gateway-test gateway-lint \
        backend-test frontend-lint docker-up docker-down

GATEWAY_DIR  := gateway
BACKEND_DIR  := backend
FRONTEND_DIR := frontend
VERSION      := $(shell grep 'version' $(GATEWAY_DIR)/pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Install ──────────────────────────────────────────────────
install: ## Install all dependencies
	cd $(GATEWAY_DIR) && pip install -e ".[dev]"
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm ci

# ── Lint ─────────────────────────────────────────────────────
gateway-lint: ## Lint gateway Python code
	cd $(GATEWAY_DIR) && python -m ruff check src/ tests/

frontend-lint: ## Lint frontend JS/JSX code
	cd $(FRONTEND_DIR) && npm run lint

lint: gateway-lint ## Run all linters

# ── Test ─────────────────────────────────────────────────────
gateway-test: ## Run gateway tests
	cd $(GATEWAY_DIR) && python -m pytest tests/ -v --tb=short

backend-test: ## Run backend tests (requires PostgreSQL + Redis)
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --tb=short

test: gateway-test ## Run all tests

# ── Build ────────────────────────────────────────────────────
build: ## Build production artefacts (frontend dist, Docker images)
	cd $(FRONTEND_DIR) && npm run build
	docker compose build

# ── Debian Package ───────────────────────────────────────────
deb: ## Build the echosmart-gateway .deb package
	cd $(GATEWAY_DIR) && dpkg-buildpackage -us -uc -b
	@echo ""
	@echo "Package built — .deb file(s):"
	@ls -1 echosmart-gateway_*.deb 2>/dev/null || echo "  (check parent directory)"

# ── Docker ───────────────────────────────────────────────────
docker-up: ## Start all services via Docker Compose
	docker compose up -d

docker-down: ## Stop all Docker Compose services
	docker compose down

# ── Clean ────────────────────────────────────────────────────
clean: ## Remove build artefacts
	rm -rf $(GATEWAY_DIR)/build $(GATEWAY_DIR)/dist $(GATEWAY_DIR)/*.egg-info
	rm -rf $(FRONTEND_DIR)/dist
	rm -f echosmart-gateway_*.deb echosmart-gateway_*.changes echosmart-gateway_*.buildinfo
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
