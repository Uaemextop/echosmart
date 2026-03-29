.PHONY: help test coverage lint format run clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	cd .. && python -m pytest gateway/tests/ -v

coverage:  ## Run tests with coverage report
	cd .. && python -m pytest gateway/tests/ --cov=gateway/src --cov-report=term-missing

lint:  ## Check code style (flake8 + mypy)
	@echo "--- flake8 ---" && flake8 src/ --max-line-length=120 --ignore=E501 || true
	@echo "--- mypy ---" && mypy src/ --ignore-missing-imports || true

format:  ## Auto-format code (black + isort)
	black src/ tests/ main.py --line-length 120
	isort src/ tests/ main.py --profile black

run:  ## Start the gateway (simulation mode)
	SIMULATION_MODE=true python main.py

clean:  ## Remove generated files
	rm -f echosmart_local.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
