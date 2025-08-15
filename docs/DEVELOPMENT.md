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
