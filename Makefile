.PHONY: help setup install install-dev test test-unit test-integration test-e2e coverage lint format typecheck security clean run run-docker build-docker docker-up docker-down

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)WebTestool - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	python -m venv venv
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo "$(YELLOW)Activate it with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)$(NC)"

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	python -m playwright install chromium
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "$(GREEN)✓ Development setup complete$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	pytest tests/e2e/ -v

coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "→ flake8"
	@flake8 . || true
	@echo "→ pylint"
	@pylint core/ modules/ reporters/ utils/ --exit-zero || true
	@echo "→ ruff"
	@ruff check . || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black .
	isort .
	@echo "$(GREEN)✓ Code formatted$(NC)"

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	mypy . --ignore-missing-imports --no-strict-optional
	@echo "$(GREEN)✓ Type checking complete$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@echo "→ bandit"
	@bandit -r . -ll -x tests/ || true
	@echo "→ safety"
	@safety check || true
	@echo "$(GREEN)✓ Security checks complete$(NC)"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

run: ## Run WebTestool (requires URL parameter)
ifndef URL
	@echo "$(RED)Error: URL parameter required$(NC)"
	@echo "Usage: make run URL=https://example.com"
	@exit 1
endif
	@echo "$(BLUE)Running scan on $(URL)...$(NC)"
	python main.py --url $(URL) $(ARGS)

run-quick: ## Quick scan (requires URL)
ifndef URL
	@echo "$(RED)Error: URL parameter required$(NC)"
	@exit 1
endif
	@echo "$(BLUE)Running quick scan on $(URL)...$(NC)"
	python main.py --url $(URL) --profile quick

run-security: ## Security scan (requires URL)
ifndef URL
	@echo "$(RED)Error: URL parameter required$(NC)"
	@exit 1
endif
	@echo "$(BLUE)Running security scan on $(URL)...$(NC)"
	python main.py --url $(URL) --profile security --pdf

build-docker: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t webtestool:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

run-docker: ## Run WebTestool in Docker (requires URL)
ifndef URL
	@echo "$(RED)Error: URL parameter required$(NC)"
	@exit 1
endif
	@echo "$(BLUE)Running in Docker...$(NC)"
	docker run -v $(PWD)/reports:/reports webtestool:latest --url $(URL)

docker-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting Docker services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"

docker-down: ## Stop all services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs: ## Show docker-compose logs
	docker-compose logs -f

verify: format lint typecheck test ## Run all checks (format, lint, typecheck, test)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

ci: ## Run CI checks (used by GitHub Actions)
	@echo "$(BLUE)Running CI checks...$(NC)"
	pytest --cov=. --cov-report=xml
	black --check .
	isort --check-only .
	mypy . --ignore-missing-imports
	@echo "$(GREEN)✓ CI checks complete$(NC)"

.DEFAULT_GOAL := help
