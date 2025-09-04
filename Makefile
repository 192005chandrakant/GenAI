# AI-Powered Misinformation Defense Platform - Makefile
# Provides commands for development, testing, and deployment

.PHONY: help dev seed test deploy-dev deploy-prod setup-env install build clean

# Default target
help:
	@echo "AI-Powered Misinformation Defense Platform"
	@echo "=========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make dev          - Start development servers (frontend + backend)"
	@echo "  make dev-backend  - Start backend development server only"
	@echo "  make dev-frontend - Start frontend development server only"
	@echo "  make seed         - Seed database with lessons and sources"
	@echo "  make test         - Run all tests (backend + frontend)"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend- Run frontend tests only"
	@echo "  make build        - Build production images"
	@echo "  make deploy-dev   - Deploy to development environment"
	@echo "  make deploy-prod  - Deploy to production environment"
	@echo "  make setup-env    - Set up development environment"
	@echo "  make install      - Install dependencies"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make lint         - Lint code"
	@echo "  make format       - Format code"
	@echo ""

# Development commands
dev: setup-env
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo "API docs at http://localhost:8000/api/docs"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@if command -v concurrently > /dev/null; then \
		concurrently -n "backend,frontend" -c "blue,green" \
			"cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" \
			"cd frontend && npm run dev"; \
	else \
		echo "Installing concurrently for parallel execution..."; \
		npm install -g concurrently; \
		concurrently -n "backend,frontend" -c "blue,green" \
			"cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" \
			"cd frontend && npm run dev"; \
	fi

dev-backend:
	@echo "Starting backend development server..."
	@cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev

# Environment setup
setup-env:
	@echo "Setting up development environment..."
	@if [ ! -f backend/.env ]; then \
		echo "Creating backend .env file..."; \
		cp backend/env.example backend/.env; \
		echo "Please edit backend/.env with your configuration"; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		echo "Creating frontend .env.local file..."; \
		cp frontend/.env.example frontend/.env.local; \
		echo "Please edit frontend/.env.local with your configuration"; \
	fi
	@echo "Environment files ready!"

# Installation
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

# Database seeding
seed:
	@echo "Seeding database with initial data..."
	@cd backend && python scripts/seed.py

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm run test

test-e2e:
	@echo "Running end-to-end tests..."
	@cd frontend && npm run test:e2e

# Code quality
lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting backend code..."
	@cd backend && flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	@cd backend && mypy app/ --ignore-missing-imports

lint-frontend:
	@echo "Linting frontend code..."
	@cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
	@echo "Formatting backend code..."
	@cd backend && black app/ tests/
	@cd backend && isort app/ tests/

format-frontend:
	@echo "Formatting frontend code..."
	@cd frontend && npm run format

# Build
build: build-backend build-frontend

build-backend:
	@echo "Building backend Docker image..."
	@docker build -f backend/Dockerfile -t misinformation-backend:latest backend/

build-frontend:
	@echo "Building frontend..."
	@cd frontend && npm run build

build-docker:
	@echo "Building all Docker images..."
	@docker-compose build

# Deployment
deploy-dev:
	@echo "Deploying to development environment..."
	@echo "Building and deploying backend to Cloud Run..."
	@cd backend && gcloud run deploy misinformation-backend-dev \
		--source . \
		--platform managed \
		--region us-central1 \
		--allow-unauthenticated \
		--set-env-vars "USE_MOCKS=false"
	@echo "Building and deploying frontend..."
	@cd frontend && npm run build
	@cd frontend && firebase deploy --project your-project-dev

deploy-prod:
	@echo "Deploying to production environment..."
	@echo "Warning: This will deploy to production!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Deploying to production..."; \
		cd backend && gcloud run deploy misinformation-backend \
			--source . \
			--platform managed \
			--region us-central1 \
			--allow-unauthenticated; \
		cd frontend && npm run build && firebase deploy --project your-project-prod; \
	else \
		echo "Deployment cancelled."; \
	fi

# Docker development
docker-dev:
	@echo "Starting development environment with Docker..."
	@docker-compose up --build

docker-dev-detached:
	@echo "Starting development environment with Docker (detached)..."
	@docker-compose up --build -d

docker-down:
	@echo "Stopping Docker development environment..."
	@docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	@docker-compose logs -f

# Database operations
db-reset:
	@echo "Resetting development database..."
	@cd backend && python scripts/reset_db.py

db-migrate:
	@echo "Running database migrations..."
	@cd backend && python scripts/migrate.py

# Utilities
clean:
	@echo "Cleaning build artifacts..."
	@cd frontend && rm -rf .next node_modules/.cache
	@cd backend && rm -rf __pycache__ .pytest_cache htmlcov
	@docker system prune -f

logs-backend:
	@echo "Showing backend logs..."
	@gcloud logs read --service=misinformation-backend --limit=50

logs-frontend:
	@echo "Showing frontend logs..."
	@firebase functions:log

health-check:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool

# Performance testing
load-test:
	@echo "Running load tests..."
	@cd tests && python load_test.py

# Export API documentation
export-docs:
	@echo "Exporting API documentation..."
	@cd backend && python scripts/export_postman_collection.py

# Security scanning
security-scan:
	@echo "Running security scans..."
	@cd backend && safety check
	@cd frontend && npm audit

# Backup
backup-dev:
	@echo "Creating backup of development data..."
	@gcloud firestore export gs://your-backup-bucket/dev-backup-$(shell date +%Y%m%d)

backup-prod:
	@echo "Creating backup of production data..."
	@gcloud firestore export gs://your-backup-bucket/prod-backup-$(shell date +%Y%m%d)

# Monitoring
monitor:
	@echo "Opening monitoring dashboard..."
	@open "https://console.cloud.google.com/monitoring"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	@cd backend && pip-compile requirements.in
	@cd frontend && npm update

# Shortcuts for common development tasks
start: dev
stop: docker-down
restart: docker-down docker-dev

# Environment-specific commands
dev-with-mocks:
	@echo "Starting development with mocks enabled..."
	@cd backend && USE_MOCKS=true python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@cd frontend && npm run dev

# Help for specific environments
help-dev:
	@echo "Development Environment Help"
	@echo "============================"
	@echo ""
	@echo "Quick start:"
	@echo "  1. make setup-env    # Set up environment files"
	@echo "  2. make install      # Install dependencies"
	@echo "  3. make dev          # Start development servers"
	@echo ""
	@echo "For development without GCP:"
	@echo "  make dev-with-mocks  # Uses local mocks"
	@echo ""

help-deploy:
	@echo "Deployment Help"
	@echo "==============="
	@echo ""
	@echo "Before deploying:"
	@echo "  1. make test         # Run all tests"
	@echo "  2. make lint         # Check code quality"
	@echo "  3. make build        # Test build process"
	@echo ""
	@echo "Deploy to development:"
	@echo "  make deploy-dev"
	@echo ""
	@echo "Deploy to production:"
	@echo "  make deploy-prod     # Interactive confirmation"
	@echo ""

# Git hooks
install-hooks:
	@echo "Installing git hooks..."
	@echo "#!/bin/sh\nmake lint" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed!"

# Documentation generation
docs:
	@echo "Generating documentation..."
	@cd backend && python -c "import app.main; print('Backend API docs at http://localhost:8000/api/docs')"
	@echo "Opening documentation..."
	@open http://localhost:8000/api/docs

# Version management
version:
	@echo "Current version information:"
	@cd backend && python -c "from app.core.config import settings; print(f'Backend: {settings.version}')"
	@cd frontend && node -p "require('./package.json').version"

# Complete setup for new developers
setup-new-dev:
	@echo "Setting up environment for new developer..."
	@make setup-env
	@make install
	@make seed
	@echo ""
	@echo "Setup complete! You can now run 'make dev' to start development."
	@echo "Visit http://localhost:3000 for the frontend and http://localhost:8000/api/docs for API docs."
