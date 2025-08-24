# Makefile для проекта Kommuna
# Удобные команды для разработки и деплоя

.PHONY: help setup up down build logs clean restart

# Цвета для красивого вывода
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
NC=\033[0m # No Color

# Показать доступные команды
help:
	@echo "$(CYAN)🚀 Kommuna Project - Доступные команды:$(NC)"
	@echo ""
	@echo "$(GREEN)📦 Настройка:$(NC)"
	@echo "  make setup        - Первоначальная настройка проекта"
	@echo "  make build        - Собрать все Docker образы"
	@echo ""
	@echo "$(GREEN)🏃 Запуск:$(NC)"
	@echo "  make up           - Запустить все сервисы"
	@echo "  make down         - Остановить все сервисы"
	@echo "  make restart      - Перезапустить все сервисы"
	@echo ""
	@echo "$(GREEN)🔧 Разработка:$(NC)"
	@echo "  make logs         - Показать логи всех сервисов"
	@echo "  make logs-backend - Логи backend сервиса"
	@echo "  make logs-bot     - Логи bot сервиса"
	@echo "  make logs-db      - Логи базы данных"
	@echo ""
	@echo "$(GREEN)🗄️ База данных:$(NC)"
	@echo "  make db-shell     - Подключиться к PostgreSQL"
	@echo "  make db-reset     - Сбросить базу данных"
	@echo ""
	@echo "$(GREEN)🧹 Очистка:$(NC)"
	@echo "  make clean        - Очистить Docker ресурсы"
	@echo "  make clean-all    - Полная очистка (включая volumes)"
	@echo ""

# Первоначальная настройка проекта
setup:
	@echo "$(YELLOW)📝 Настройка проекта Kommuna...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Создан файл .env$(NC)"; \
		echo "$(RED)⚠️  ВАЖНО: Отредактируйте .env файл с вашими настройками!$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  Файл .env уже существует$(NC)"; \
	fi
	@mkdir -p logs database/init bot/logs backend/logs
	@echo "$(GREEN)✅ Директории созданы$(NC)"
	@echo "$(PURPLE)🎯 Настройка завершена! Теперь:$(NC)"
	@echo "$(PURPLE)   1. Отредактируйте .env файл$(NC)"
	@echo "$(PURPLE)   2. Запустите: make up$(NC)"

# Собрать все Docker образы
build:
	@echo "$(YELLOW)🔨 Сборка Docker образов...$(NC)"
	docker-compose build

# Запустить все сервисы
up:
	@echo "$(YELLOW)🚀 Запуск сервисов...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Сервисы запущены!$(NC)"
	@echo "$(CYAN)🌐 Frontend: http://localhost:3000$(NC)"
	@echo "$(CYAN)🔧 Backend API: http://localhost:8000$(NC)"
	@echo "$(CYAN)📊 Docs: http://localhost:8000/docs$(NC)"

# Остановить все сервисы
down:
	@echo "$(YELLOW)⏹️  Остановка сервисов...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Сервисы остановлены$(NC)"

# Перезапустить все сервисы
restart: down up
	@echo "$(GREEN)🔄 Сервисы перезапущены$(NC)"

# Показать логи всех сервисов
logs:
	docker-compose logs -f

# Логи отдельных сервисов
logs-backend:
	docker-compose logs -f backend

logs-bot:
	docker-compose logs -f bot

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

# Подключиться к базе данных
db-shell:
	@echo "$(YELLOW)💾 Подключение к PostgreSQL...$(NC)"
	docker-compose exec postgres psql -U $${DB_USER:-postgres} -d $${DB_NAME:-kommuna}

# Сбросить базу данных
db-reset:
	@echo "$(RED)⚠️  Это удалит ВСЕ данные в базе!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(YELLOW)🗑️  Сброс базы данных...$(NC)"; \
		docker-compose down; \
		docker volume rm kommuna_postgres_data 2>/dev/null || true; \
		echo "$(GREEN)✅ База данных сброшена$(NC)"; \
	else \
		echo "$(BLUE)❌ Отменено$(NC)"; \
	fi

# Очистка Docker ресурсов
clean:
	@echo "$(YELLOW)🧹 Очистка неиспользуемых Docker ресурсов...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Полная очистка включая volumes
clean-all:
	@echo "$(RED)⚠️  Это удалит ВСЕ данные проекта!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(YELLOW)🗑️  Полная очистка...$(NC)"; \
		docker-compose down -v; \
		docker system prune -af; \
		echo "$(GREEN)✅ Полная очистка завершена$(NC)"; \
	else \
		echo "$(BLUE)❌ Отменено$(NC)"; \
	fi

# Показать статус сервисов
status:
	@echo "$(CYAN)📊 Статус сервисов:$(NC)"
	docker-compose ps

# Обновить проект
update: down build up
	@echo "$(GREEN)🔄 Проект обновлен!$(NC)"

# Показать информацию о ресурсах
stats:
	@echo "$(CYAN)📈 Использование ресурсов:$(NC)"
	docker stats --no-stream

# Резервная копия базы данных
backup:
	@mkdir -p backups
	@echo "$(YELLOW)💾 Создание резервной копии...$(NC)"
	docker-compose exec postgres pg_dump -U $${DB_USER:-postgres} $${DB_NAME:-kommuna} > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Резервная копия создана в папке backups/$(NC)"

# По умолчанию показываем help
.DEFAULT_GOAL := help