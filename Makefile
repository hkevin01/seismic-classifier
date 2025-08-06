# Seismic Classifier - Universal Docker Development Makefile
# Provides consistent commands across all development environments

.PHONY: help dev-up dev-down dev-restart dev-logs dev-shell test lint format clean build deploy

# Default target
help: ## Show this help message
	@echo "🌊 Seismic Classifier Development Commands"
	@echo ""
	@echo "Core Development:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Environment Management
dev-up: ## Start all development services
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d dev-backend dev-frontend dev-db dev-redis
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📊 API Docs: http://localhost:8000/docs"
	@echo "📓 Jupyter: http://localhost:8888"

dev-up-full: ## Start all services including analytics and storage
	@echo "🚀 Starting full development environment..."
	docker-compose -f docker-compose.dev.yml --profile analytics --profile storage up -d
	@echo "✅ Full development environment started!"
	@make dev-status

dev-down: ## Stop all development services
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Development environment stopped!"

dev-restart: ## Restart development services
	@echo "🔄 Restarting development environment..."
	@make dev-down
	@make dev-up

dev-rebuild: ## Rebuild and restart development containers
	@echo "🔨 Rebuilding development containers..."
	docker-compose -f docker-compose.dev.yml build --no-cache
	@make dev-restart

dev-logs: ## Show logs from all development services
	docker-compose -f docker-compose.dev.yml logs -f

dev-status: ## Show status of all development services
	@echo "📊 Development Environment Status:"
	@docker-compose -f docker-compose.dev.yml ps
	@echo ""
	@echo "🔗 Service URLs:"
	@echo "  Frontend:     http://localhost:3000"
	@echo "  Backend API:  http://localhost:8000"
	@echo "  API Docs:     http://localhost:8000/docs"
	@echo "  Jupyter:      http://localhost:8888"
	@echo "  Database:     postgresql://postgres:password@localhost:5432/seismic_dev"
	@echo "  Redis:        redis://localhost:6379/0"

# Development Shells
dev-shell: ## Open shell in backend development container
	@echo "🐚 Opening backend development shell..."
	docker-compose -f docker-compose.dev.yml exec dev-backend bash

frontend-shell: ## Open shell in frontend development container
	@echo "🐚 Opening frontend development shell..."
	docker-compose -f docker-compose.dev.yml exec dev-frontend bash

tools-shell: ## Open shell in tools container
	@echo "🔧 Opening tools development shell..."
	docker-compose -f docker-compose.dev.yml run --rm dev-tools bash

db-shell: ## Open PostgreSQL shell
	@echo "🗄️ Opening database shell..."
	docker-compose -f docker-compose.dev.yml exec dev-db psql -U postgres -d seismic_dev

redis-shell: ## Open Redis CLI
	@echo "🔴 Opening Redis shell..."
	docker-compose -f docker-compose.dev.yml exec dev-redis redis-cli

# Code Quality and Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	docker-compose -f docker-compose.dev.yml exec dev-backend python -m pytest tests/ -v --cov=src/seismic_classifier --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/"

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	docker-compose -f docker-compose.dev.yml exec dev-backend python -m pytest tests/ -v --cov=src/seismic_classifier -f

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	docker-compose -f docker-compose.dev.yml exec dev-frontend npm test

lint: ## Run code quality checks
	@echo "🔍 Running code quality checks..."
	docker-compose -f docker-compose.dev.yml run --rm dev-tools black --check src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools flake8 src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools mypy src/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools bandit -r src/
	@echo "✅ Code quality checks completed!"

lint-fix: ## Fix code quality issues
	@echo "🔧 Fixing code quality issues..."
	docker-compose -f docker-compose.dev.yml run --rm dev-tools black src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools isort src/ tests/
	@echo "✅ Code quality issues fixed!"

format: ## Format all code
	@echo "🎨 Formatting code..."
	docker-compose -f docker-compose.dev.yml exec dev-backend black src/ tests/
	docker-compose -f docker-compose.dev.yml exec dev-backend isort src/ tests/
	docker-compose -f docker-compose.dev.yml exec dev-frontend npm run format
	@echo "✅ Code formatted!"

security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	docker-compose -f docker-compose.dev.yml run --rm dev-tools bandit -r src/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools safety check
	docker-compose -f docker-compose.dev.yml run --rm dev-tools trivy fs .
	@echo "✅ Security scans completed!"

# Database Management
db-reset: ## Reset development database
	@echo "🗄️ Resetting development database..."
	docker-compose -f docker-compose.dev.yml stop dev-db
	docker volume rm seismic-dev-db-data || true
	docker-compose -f docker-compose.dev.yml up -d dev-db
	@echo "⏳ Waiting for database to be ready..."
	@sleep 10
	@make db-migrate
	@echo "✅ Database reset completed!"

db-migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."
	docker-compose -f docker-compose.dev.yml exec dev-backend alembic upgrade head
	@echo "✅ Database migrations completed!"

db-migration: ## Create new database migration
	@read -p "Enter migration message: " msg; \
	docker-compose -f docker-compose.dev.yml exec dev-backend alembic revision --autogenerate -m "$$msg"

db-backup: ## Backup development database
	@echo "💾 Backing up development database..."
	docker-compose -f docker-compose.dev.yml exec dev-db pg_dump -U postgres seismic_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backup completed!"

# Development Utilities
install-deps: ## Install/update dependencies
	@echo "📦 Installing dependencies..."
	docker-compose -f docker-compose.dev.yml exec dev-backend pip install -e . --upgrade
	docker-compose -f docker-compose.dev.yml exec dev-frontend npm install
	@echo "✅ Dependencies installed!"

jupyter: ## Start Jupyter notebook server
	@echo "📓 Starting Jupyter notebook..."
	docker-compose -f docker-compose.dev.yml exec dev-backend jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
	@echo "🌐 Jupyter available at: http://localhost:8888"

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	docker-compose -f docker-compose.dev.yml exec dev-backend sphinx-build -b html docs/ docs/_build/html
	@echo "📖 Documentation available at: docs/_build/html/index.html"

clean: ## Clean development environment
	@echo "🧹 Cleaning development environment..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "✅ Development environment cleaned!"

# Production Building
build: ## Build production containers
	@echo "🏗️ Building production containers..."
	docker build -t seismic-classifier:latest .
	@echo "✅ Production containers built!"

# CI/CD
ci-test: ## Run CI tests
	@echo "🔄 Running CI tests..."
	docker-compose -f docker-compose.dev.yml run --rm dev-tools python -m pytest tests/ -v --cov=src/seismic_classifier --cov-report=xml
	docker-compose -f docker-compose.dev.yml run --rm dev-tools black --check src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools flake8 src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools mypy src/
	docker-compose -f docker-compose.dev.yml run --rm dev-tools bandit -r src/
	@echo "✅ CI tests completed!"

# Quick Development Commands
quick-start: ## Quick start for new developers
	@echo "🚀 Quick start for new developers..."
	@make dev-up
	@make install-deps
	@make db-migrate
	@make test
	@echo "🎉 Ready to develop! Check http://localhost:3000 and http://localhost:8000"

# Monitoring
logs-backend: ## Show backend logs
	docker-compose -f docker-compose.dev.yml logs -f dev-backend

logs-frontend: ## Show frontend logs
	docker-compose -f docker-compose.dev.yml logs -f dev-frontend

logs-db: ## Show database logs
	docker-compose -f docker-compose.dev.yml logs -f dev-db

health-check: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"
	@docker-compose -f docker-compose.dev.yml exec dev-db pg_isready -U postgres && echo "✅ Database healthy" || echo "❌ Database unhealthy"
	@docker-compose -f docker-compose.dev.yml exec dev-redis redis-cli ping && echo "✅ Redis healthy" || echo "❌ Redis unhealthy"

# Legacy support (for backward compatibility)
venv: dev-up ## Legacy: Start development environment
setup: quick-start ## Legacy: Complete project setup
install: install-deps ## Legacy: Install dependencies
