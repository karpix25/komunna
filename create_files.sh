#!/bin/bash

echo "🚀 Создание всех файлов проекта..."

# ===========================================
# КОРНЕВЫЕ ФАЙЛЫ
# ===========================================

# .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
*/node_modules/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
*/.env
*/.env.local

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Database
*.db
*.sqlite
postgres_data/
redis_data/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# Coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Backup files
*.backup
*.bak

# Temporary files
tmp/
temp/
EOF

# .env.example
cat > .env.example << 'EOF'
# Database Configuration
POSTGRES_DB=myapp
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://myapp_user:your_secure_password_here@localhost:5432/myapp

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Backend Configuration
SECRET_KEY=your_super_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MyApp

# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook

# Monitoring & Logging
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# Email Configuration (if needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password

# File Storage (if using cloud storage)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_BUCKET_NAME=your_bucket_name
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: myapp_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-myapp}
      POSTGRES_USER: ${POSTGRES_USER:-myapp_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - myapp_network

  redis:
    image: redis:7-alpine
    container_name: myapp_redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - myapp_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: myapp_backend
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-myapp_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-myapp}
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG:-false}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - myapp_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: myapp_frontend
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      - NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME:-MyApp}
    depends_on:
      - backend
    ports:
      - "3000:3000"
    restart: unless-stopped
    networks:
      - myapp_network

  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    container_name: myapp_bot
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - API_URL=http://backend:8000
      - DATABASE_URL=postgresql://${POSTGRES_USER:-myapp_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-myapp}
      - WEBHOOK_URL=${WEBHOOK_URL}
    depends_on:
      - postgres
      - backend
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - myapp_network

  nginx:
    image: nginx:alpine
    container_name: myapp_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - myapp_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  myapp_network:
    driver: bridge
EOF

# docker-compose.dev.yml
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: myapp_postgres_dev
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - myapp_dev_network

  redis:
    image: redis:7-alpine
    container_name: myapp_redis_dev
    ports:
      - "6380:6379"
    volumes:
      - redis_dev_data:/data
    networks:
      - myapp_dev_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: myapp_backend_dev
    environment:
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/myapp_dev
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./backend/src:/app/src
      - ./logs:/app/logs
    ports:
      - "8001:8000"
    depends_on:
      - postgres
      - redis
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - myapp_dev_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: myapp_frontend_dev
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
      - NEXT_PUBLIC_APP_NAME=MyApp Dev
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - ./frontend/package.json:/app/package.json
    ports:
      - "3001:3000"
    command: npm run dev
    networks:
      - myapp_dev_network

  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile.dev
    container_name: myapp_bot_dev
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - API_URL=http://backend:8000
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/myapp_dev
      - DEBUG=true
    volumes:
      - ./bot/src:/app/src
      - ./logs:/app/logs
    depends_on:
      - postgres
      - backend
    networks:
      - myapp_dev_network

volumes:
  postgres_dev_data:
    driver: local
  redis_dev_data:
    driver: local

networks:
  myapp_dev_network:
    driver: bridge
EOF

# Makefile
cat > Makefile << 'EOF'
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
EOF

# README.md
cat > README.md << 'EOF'
# MyApp - Полнофункциональное веб-приложение

Современное веб-приложение с Next.js фронтендом, Python (FastAPI) бэкендом и Telegram ботом.

## 🚀 Быстрый старт

### Первоначальная настройка
```bash
git clone <your-repo-url>
cd myapp
make setup
```

### Запуск в режиме разработки
```bash
make dev
```

### Доступ к сервисам
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001
- Database: localhost:5433

## 📁 Структура проекта

```
myapp/
├── frontend/          # Next.js приложение
├── backend/           # FastAPI сервер
├── bot/              # Telegram бот
├── nginx/            # Nginx конфигурация
├── scripts/          # Утилиты
└── docs/            # Документация
```

## 🛠️ Команды разработки

```bash
make dev              # Запуск dev среды
make prod            # Запуск prod среды
make test            # Запуск всех тестов
make logs            # Просмотр логов
make clean           # Очистка контейнеров
```

## 📚 Документация

- [API Documentation](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

См. [CONTRIBUTING.md](docs/CONTRIBUTING.md) для деталей по разработке.

## 📄 License

MIT License
EOF

# easypanel.json
cat > easypanel.json << 'EOF'
{
  "name": "myapp",
  "services": [
    {
      "name": "postgres",
      "type": "postgres",
      "version": "15",
      "envVars": {
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "myapp_user",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
      },
      "volumes": [
        {
          "name": "postgres-data",
          "mountPath": "/var/lib/postgresql/data"
        }
      ]
    },
    {
      "name": "redis",
      "type": "redis",
      "version": "7"
    },
    {
      "name": "backend",
      "type": "app",
      "source": {
        "type": "docker",
        "dockerfilePath": "./backend/Dockerfile"
      },
      "domains": [
        {
          "name": "api.yourdomain.com"
        }
      ],
      "envVars": {
        "DATABASE_URL": "postgresql://myapp_user:${POSTGRES_PASSWORD}@postgres:5432/myapp",
        "REDIS_URL": "redis://redis:6379"
      },
      "ports": [
        {
          "published": 8000,
          "target": 8000
        }
      ]
    },
    {
      "name": "frontend",
      "type": "app",
      "source": {
        "type": "docker",
        "dockerfilePath": "./frontend/Dockerfile"
      },
      "domains": [
        {
          "name": "yourdomain.com"
        }
      ],
      "envVars": {
        "NEXT_PUBLIC_API_URL": "https://api.yourdomain.com"
      },
      "ports": [
        {
          "published": 3000,
          "target": 3000
        }
      ]
    },
    {
      "name": "bot",
      "type": "app",
      "source": {
        "type": "docker",
        "dockerfilePath": "./bot/Dockerfile"
      },
      "envVars": {
        "BOT_TOKEN": "${BOT_TOKEN}",
        "API_URL": "https://api.yourdomain.com",
        "DATABASE_URL": "postgresql://myapp_user:${POSTGRES_PASSWORD}@postgres:5432/myapp"
      }
    }
  ]
}
EOF

# ===========================================
# FRONTEND FILES
# ===========================================

# frontend/package.json
cat > frontend/package.json << 'EOF'
{
  "name": "myapp-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "test": "jest",
    "test:watch": "jest --watch",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "18.0.0",
    "react-dom": "18.0.0",
    "@types/node": "20.0.0",
    "@types/react": "18.0.0",
    "@types/react-dom": "18.0.0",
    "typescript": "5.0.0",
    "tailwindcss": "3.0.0",
    "autoprefixer": "10.0.0",
    "postcss": "8.0.0"
  },
  "devDependencies": {
    "eslint": "8.0.0",
    "eslint-config-next": "14.0.0",
    "prettier": "3.0.0",
    "jest": "29.0.0",
    "@testing-library/react": "13.0.0",
    "@testing-library/jest-dom": "6.0.0"
  }
}
EOF

# frontend/.env.local.example
cat > frontend/.env.local.example << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MyApp
EOF

# frontend/next.config.js
cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  experimental: {
    serverActions: true,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
}

module.exports = nextConfig
EOF

# frontend/tailwind.config.js
cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}
EOF

# frontend/tsconfig.json
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# frontend/postcss.config.js
cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# frontend/Dockerfile
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
EOF

# frontend/Dockerfile.dev
cat > frontend/Dockerfile.dev << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOF

# ===========================================
# BACKEND FILES
# ===========================================

# backend/requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
loguru==0.7.2
EOF

# backend/requirements-dev.txt
cat > backend/requirements-dev.txt << 'EOF'
-r requirements.txt
black==23.11.0
flake8==6.1.0
isort==5.12.0
mypy==1.7.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pre-commit==3.5.0
EOF

# backend/.env.example
cat > backend/.env.example << 'EOF'
DATABASE_URL=postgresql://myapp_user:password@localhost:5432/myapp
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key_here
DEBUG=false
LOG_LEVEL=INFO
EOF

# backend/pyproject.toml
cat > backend/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp-backend"
version = "1.0.0"
description = "MyApp Backend API"
requires-python = ">=3.11"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
EOF

# backend/alembic.ini
cat > backend/alembic.ini << 'EOF'
# A generic, single database configuration.

[alembic]
# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format for new migration files
# version_num_format = %04d

# version number length for new migration files
# version_num_digits = 4

# set to 'true' to search source files recursively
# in each "version_locations" directory
# Also supported: space-separated list of files/directories
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# backend/pytest.ini
cat > backend/pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --strict-config --verbose
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF

# backend/Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# backend/Dockerfile.dev
cat > backend/Dockerfile.dev << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# ===========================================
# BOT FILES
# ===========================================

# bot/requirements.txt
cat > bot/requirements.txt << 'EOF'
aiogram==3.2.0
httpx==0.25.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
loguru==0.7.2
EOF

# bot/requirements-dev.txt
cat > bot/requirements-dev.txt << 'EOF'
-r requirements.txt
black==23.11.0
flake8==6.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
EOF

# bot/.env.example
cat > bot/.env.example << 'EOF'
BOT_TOKEN=your_telegram_bot_token_here
API_URL=http://localhost:8000
DATABASE_URL=postgresql://myapp_user:password@localhost:5432/myapp
WEBHOOK_URL=https://yourdomain.com/webhook
DEBUG=false
LOG_LEVEL=INFO
EOF

# bot/Dockerfile
cat > bot/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN adduser --disabled-password --gecos '' botuser
RUN chown -R botuser:botuser /app
USER botuser

CMD ["python", "-m", "src.main"]
EOF

# bot/Dockerfile.dev
cat > bot/Dockerfile.dev << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

CMD ["python", "-m", "src.main"]
EOF

# ===========================================
# NGINX FILES
# ===========================================

# nginx/nginx.conf
cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Include additional configurations
    include /etc/nginx/conf.d/*.conf;
}
EOF

# nginx/conf.d/default.conf
cat > nginx/conf.d/default.conf << 'EOF'
upstream frontend {
    server frontend:3000;
}

upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Telegram webhook
    location /webhook {
        proxy_pass http://backend/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# ===========================================
# DATABASE FILES
# ===========================================

# database/init.sql
cat > database/init.sql << 'EOF'
-- Initial database setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create basic tables
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    telegram_id BIGINT UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Insert default admin user (password: admin123)
INSERT INTO users (email, username, hashed_password, is_superuser) 
VALUES (
    'admin@example.com', 
    'admin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3fKNHjJX6i',
    true
) ON CONFLICT (email) DO NOTHING;
EOF

# ===========================================
# SCRIPTS FILES  
# ===========================================

# scripts/setup.sh
cat > scripts/setup.sh << 'EOF'
#!/bin/bash

echo "🚀 Setting up MyApp development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files from examples
echo "📝 Creating environment files..."
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p database/backups
mkdir -p nginx/ssl
mkdir -p nginx/logs

# Set executable permissions
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo "📝 Please edit the following files with your configuration:"
echo "   - .env"
echo "   - frontend/.env.local"
echo "   - backend/.env"
echo "   - bot/.env"
echo ""
echo "🚀 To start development:"
echo "   make dev"
EOF

# scripts/deploy.sh
cat > scripts/deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying MyApp..."

# Build production images
echo "🔨 Building production images..."
docker-compose -f docker-compose.yml build

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.yml run --rm backend alembic upgrade head

# Start services
echo "🏃 Starting services..."
docker-compose -f docker-compose.yml up -d

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
EOF

# scripts/backup-db.sh
cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="./database/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "🗄️ Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
docker-compose exec postgres pg_dump -U ${POSTGRES_USER:-myapp_user} ${POSTGRES_DB:-myapp} > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t $BACKUP_DIR/backup_*.sql | tail -n +11 | xargs -r rm
    echo "🧹 Old backups cleaned up"
else
    echo "❌ Backup failed"
    exit 1
fi
EOF

# scripts/restore-db.sh
cat > scripts/restore-db.sh << 'EOF'
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la ./database/backups/
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restoring database from: $BACKUP_FILE"

# Stop services that use database
docker-compose stop backend bot

# Restore database
docker-compose exec postgres psql -U ${POSTGRES_USER:-myapp_user} -d ${POSTGRES_DB:-myapp} < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully"
    
    # Restart services
    docker-compose start backend bot
    echo "🚀 Services restarted"
else
    echo "❌ Database restore failed"
    exit 1
fi
EOF

# ===========================================
# DOCUMENTATION FILES
# ===========================================

# docs/API.md
cat > docs/API.md << 'EOF'
# API Documentation

## Base URL
- Development: `http://localhost:8001`
- Production: `https://api.yourdomain.com`

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### Users
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update current user
- `GET /users/{user_id}` - Get user by ID (admin only)

### Health Check
- `GET /health` - Health check endpoint

## Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success"
}
```

## Error Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```
EOF

# docs/DEVELOPMENT.md
cat > docs/DEVELOPMENT.md << 'EOF'
# Development Guide

## Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Getting Started

1. Clone the repository
2. Run initial setup: `make setup`
3. Start development environment: `make dev`

## Development Workflow

### Working with Frontend
```bash
# Start only frontend for development
docker-compose -f docker-compose.dev.yml up frontend

# Or run locally
cd frontend
npm install
npm run dev
```

### Working with Backend
```bash
# Start only backend for development
docker-compose -f docker-compose.dev.yml up backend

# Or run locally
cd backend
pip install -r requirements-dev.txt
uvicorn src.main:app --reload
```

### Working with Bot
```bash
# Start only bot for development
docker-compose -f docker-compose.dev.yml up bot

# Or run locally
cd bot
pip install -r requirements-dev.txt
python -m src.main
```

## Database Migrations

### Create Migration
```bash
docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "Add new table"
```

### Apply Migrations
```bash
make db-migrate ENV=dev
```

## Testing

### Run All Tests
```bash
make test ENV=dev
```

### Run Specific Tests
```bash
make test-backend ENV=dev
make test-frontend ENV=dev
make test-bot ENV=dev
```

## Code Quality

### Format Code
```bash
make format ENV=dev
```

### Lint Code
```bash
make lint ENV=dev
```

## Environment Variables

### Development
- Copy `.env.example` to `.env`
- Copy service-specific `.env.example` files

### Required Variables
- `POSTGRES_PASSWORD` - Database password
- `SECRET_KEY` - JWT secret key
- `BOT_TOKEN` - Telegram bot token

## Debugging

### View Logs
```bash
make dev-logs
```

### Access Container Shell
```bash
docker-compose -f docker-compose.dev.yml exec backend bash
docker-compose -f docker-compose.dev.yml exec frontend sh
docker-compose -f docker-compose.dev.yml exec bot bash
```

## Database Access
```bash
# Connect to development database
docker-compose -f docker-compose.dev.yml exec postgres psql -U dev_user -d myapp_dev
```
EOF

# docs/DEPLOYMENT.md
cat > docs/DEPLOYMENT.md << 'EOF'
# Deployment Guide

## EasyPanel Deployment

1. Create new project in EasyPanel
2. Upload `easypanel.json` configuration
3. Set environment variables
4. Deploy services

### Required Environment Variables
```
POSTGRES_PASSWORD=secure_password_here
SECRET_KEY=your_jwt_secret_key
BOT_TOKEN=your_telegram_bot_token
```

## Manual Server Deployment

### Prerequisites
- Docker and Docker Compose
- SSL certificates (for HTTPS)
- Domain name pointing to server

### Steps

1. Clone repository on server
```bash
git clone <repository_url>
cd myapp
```

2. Configure environment
```bash
cp .env.example .env
# Edit .env with production values
```

3. Setup SSL certificates
```bash
# Copy SSL certificates to nginx/ssl/
cp your_cert.pem nginx/ssl/
cp your_key.key nginx/ssl/
```

4. Deploy
```bash
make deploy
```

### Production Checklist
- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Database backups scheduled
- [ ] Monitoring setup
- [ ] Domain DNS configured
- [ ] Firewall rules applied

## Database Backup

### Automatic Backups
Setup cron job for automatic backups:
```bash
# Add to crontab
0 2 * * * /path/to/project/scripts/backup-db.sh
```

### Manual Backup
```bash
make backup
```

### Restore Backup
```bash
make restore FILE=./database/backups/backup_20231201_020000.sql
```

## Monitoring

### Logs Location
- Application logs: `./logs/`
- Nginx logs: `./nginx/logs/`
- Docker logs: `docker-compose logs`

### Health Checks
- Frontend: `http://yourdomain.com`
- Backend API: `http://api.yourdomain.com/health`
- Database: Check container status

## Scaling

### Horizontal Scaling
1. Setup load balancer
2. Deploy multiple backend instances
3. Use shared Redis for sessions
4. Setup database replication

### Performance Optimization
1. Enable Redis caching
2. Optimize database queries
3. Setup CDN for static assets
4. Enable gzip compression
EOF

# docs/CONTRIBUTING.md
cat > docs/CONTRIBUTING.md << 'EOF'
# Contributing Guide

## Development Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Branch Naming
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/urgent-fix` - Urgent production fixes

## Commit Messages
Follow conventional commits format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Code Style

### Python (Backend/Bot)
- Follow PEP 8
- Use Black for formatting
- Use type hints
- Write docstrings for functions

### TypeScript/React (Frontend)
- Use ESLint and Prettier
- Follow React best practices
- Use TypeScript strictly
- Write component documentation

## Testing Requirements
- Write unit tests for new features
- Ensure all tests pass
- Maintain test coverage above 80%

## Pull Request Process
1. Update documentation
2. Add tests for new features
3. Ensure CI passes
4. Request review from maintainers
5. Address review feedback

## Local Development Setup
See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

## Questions?
Open an issue or contact the maintainers.
EOF

# ===========================================
# EXAMPLE SOURCE FILES
# ===========================================

# Create basic source file examples
mkdir -p frontend/src/app
mkdir -p backend/src
mkdir -p bot/src

# frontend/src/app/page.tsx
cat > frontend/src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">Welcome to MyApp</h1>
        <p className="text-lg">Your full-stack application template</p>
      </div>
    </main>
  )
}
EOF

# backend/src/__init__.py
touch backend/src/__init__.py

# backend/src/main.py
cat > backend/src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MyApp API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to MyApp API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# bot/src/__init__.py
touch bot/src/__init__.py

# bot/src/main.py
cat > bot/src/main.py << 'EOF'
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token (replace with your token)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    """Handle /start command"""
    await message.answer("Hello! Welcome to MyApp Bot!")

async def main():
    """Main function to start the bot"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Set executable permissions for scripts
chmod +x scripts/setup.sh scripts/deploy.sh scripts/backup-db.sh scripts/restore-db.sh

echo "✅ Все файлы созданы успешно!"
echo ""
echo "🚀 Следующие шаги:"
echo "1. Выполните: make setup"
echo "2. Отредактируйте .env файлы"
echo "3. Запустите: make dev"
echo ""
echo "📁 Созданные файлы:"
echo "├── Корневые конфигурационные файлы"
echo "├── Frontend (Next.js) файлы"
echo "├── Backend (FastAPI) файлы"
echo "├── Bot (Aiogram) файлы"
echo "├── Nginx конфигурация"
echo "├── Database файлы"
echo "├── Scripts для автоматизации"
echo "└── Документация"