.PHONY: help build up down logs clean dev prod test lint format

# Default environment
ENV ?= dev

help: ## Show this help message
	@echo 'Usage: make [target] [ENV=dev|prod]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up the project..."
	@cp .env.example .env
	@cp frontend/.env.local.example frontend/.env.local
	@cp backend/.env.example backend/.env
	@cp bot/.env.example bot/.env
	@chmod +x scripts/*.sh
	@echo "✅ Project setup complete!"
	@echo "📝 Please edit .env files with your configuration"

build: ## Build all services
	docker-compose -f docker-compose.$(ENV).yml build

up: ## Start all services
	docker-compose -f docker-compose.$(ENV).yml up -d

down: ## Stop all services
	docker-compose -f docker-compose.$(ENV).yml down

logs: ## View logs for all services
	docker-compose -f docker-compose.$(ENV).yml logs -f

restart: ## Restart all services
	make down ENV=$(ENV)
	make up ENV=$(ENV)

clean: ## Remove all containers, networks, and volumes
	docker-compose -f docker-compose.$(ENV).yml down -v --remove-orphans
	docker system prune -a -f

# Development commands
dev: ## Start development environment
	make up ENV=dev

dev-logs: ## View development logs
	make logs ENV=dev

dev-clean: ## Clean development environment
	make clean ENV=dev

# Production commands
prod: ## Start production environment
	make up ENV=prod

prod-logs: ## View production logs
	make logs ENV=prod

# Database commands
db-migrate: ## Run database migrations
	docker-compose -f docker-compose.$(ENV).yml exec backend alembic upgrade head

db-reset: ## Reset database
	docker-compose -f docker-compose.$(ENV).yml exec backend alembic downgrade base
	docker-compose -f docker-compose.$(ENV).yml exec backend alembic upgrade head

db-seed: ## Seed database with test data
	docker-compose -f docker-compose.$(ENV).yml exec backend python -m src.scripts.seed_db

# Testing commands
test: ## Run all tests
	docker-compose -f docker-compose.$(ENV).yml exec backend pytest
	docker-compose -f docker-compose.$(ENV).yml exec frontend npm test
	docker-compose -f docker-compose.$(ENV).yml exec bot python -m pytest

test-backend: ## Run backend tests
	docker-compose -f docker-compose.$(ENV).yml exec backend pytest

test-frontend: ## Run frontend tests
	docker-compose -f docker-compose.$(ENV).yml exec frontend npm test

test-bot: ## Run bot tests
	docker-compose -f docker-compose.$(ENV).yml exec bot python -m pytest

# Code quality commands
lint: ## Run linters
	docker-compose -f docker-compose.$(ENV).yml exec backend black . && flake8
	docker-compose -f docker-compose.$(ENV).yml exec frontend npm run lint
	docker-compose -f docker-compose.$(ENV).yml exec bot black . && flake8

format: ## Format code
	docker-compose -f docker-compose.$(ENV).yml exec backend black .
	docker-compose -f docker-compose.$(ENV).yml exec frontend npm run format
	docker-compose -f docker-compose.$(ENV).yml exec bot black .

# Backup and restore
backup: ## Backup database
	./scripts/backup-db.sh

restore: ## Restore database from backup
	./scripts/restore-db.sh $(FILE)

# EasyPanel deployment
deploy: ## Deploy to EasyPanel
	./scripts/deploy.sh
